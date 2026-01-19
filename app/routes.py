import os
import socket
import qrcode
from io import BytesIO
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app, abort, send_file, Response
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from app.models import File, User, Log, Folder
from app.extensions import db, bcrypt
from app.utils import log_action
from functools import wraps
from PIL import Image
import mimetypes
import unicodedata
import re

bp = Blueprint('main', __name__)

def secure_filename_unicode(filename):
    """
    Passes through Unicode characters to support multi-language filenames 
    while stripping dangerous characters.
    """
    # Normalize unicode characters to NFKD form
    filename = unicodedata.normalize("NFKD", filename)
    
    # Remove any null bytes or control characters
    filename = filename.replace('\0', '')
    
    # Allow alphanumeric (including unicode), dashes, underscores, dots, and spaces
    # This regex matches characters that are NOT:
    # \w (alphanumeric + underscore in any language), \s (whitespace), - (dash), . (dot)
    filename = re.sub(r'[^\w\s\-\.]', '', filename)
    
    # Strip leading/trailing whitespace
    filename = filename.strip()
    
    # Replace sequences of whitespace with a single underscore to avoid messy URLs
    filename = re.sub(r'[-\s]+', '_', filename)
    
    return filename

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        try:
            db.session.commit()
        except:
            db.session.rollback()

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@bp.route('/qrcode')
@login_required
def generate_qr():
    # Get the server's local IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "127.0.0.1"
    
    url = f"http://{local_ip}:{current_app.config.get('PORT', 5000)}"
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to BytesIO instead of file
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    
    return send_file(buf, mimetype='image/png')

@bp.route('/sw.js')
def service_worker():
    return send_from_directory(os.path.join(current_app.root_path, 'static'), 'sw.js')

@bp.route('/manifest.json')
def manifest():
    return send_from_directory(os.path.join(current_app.root_path, 'static'), 'manifest.json')

@bp.route('/dashboard')
@login_required
def dashboard():
    folder_id = request.args.get('folder_id', type=int)
    current_folder = None
    
    if folder_id:
        current_folder = Folder.query.get_or_404(folder_id)
        # Ensure user can access this folder: Owner OR Public OR Admin
        if current_folder.user_id != current_user.id and not current_folder.is_public and not current_user.is_admin:
             abort(403)
             
        # Breadcrumbs (simple: just Parent -> Current)
        # For full breadcrumb, we'd need recursion, but let's stick to simple parent link
    
    # Files
    files_query = File.query.filter(
        (File.folder_id == folder_id) &
        (
            (File.is_public == True) | 
            (File.user_id == current_user.id) |
            (File.shared_with.any(User.id == current_user.id)) |
            (current_user.is_admin == True)
        )
    )
    
    # Folders visibility logic
    if current_user.is_admin:
        # Admin sees ALL folders in this parent
        folders_query = Folder.query.filter_by(parent_id=folder_id)
    else:
        # Standard user: Own folders OR Public folders
        folders_query = Folder.query.filter(
            (Folder.parent_id == folder_id) &
            (
                (Folder.user_id == current_user.id) |
                (Folder.is_public == True)
            )
        )

    files = files_query.order_by(File.upload_time.desc()).all()
    folders = folders_query.order_by(Folder.name.asc()).all()
    
    return render_template('dashboard.html', files=files, folders=folders, current_folder=current_folder)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    if current_app.config.get('OMNI_EDITION') == 'CORE':
        abort(404) # Hide admin completely in Core
    users = User.query.all()
    logs = Log.query.order_by(Log.timestamp.desc()).limit(50).all()
    files_count = File.query.count()
    
    # Active users in last 24h
    cutoff = datetime.utcnow() - timedelta(hours=24)
    active_users_count = User.query.filter(User.last_seen >= cutoff).count()
    
    return render_template('admin_dashboard.html', 
                         users=users, 
                         logs=logs, 
                         total_files=files_count, 
                         active_users_count=active_users_count)

@bp.route('/admin/create_user', methods=['POST'])
@login_required
@admin_required
def create_user():
    username = request.form.get('username')
    password = request.form.get('password')
    is_admin = request.form.get('is_admin') == 'on'
    
    # Validation
    if not username or not password:
        flash('Username and password are required.', 'danger')
        return redirect(url_for('main.admin_dashboard'))
    
    # Normalize username
    username = username.lower()
        
    if User.query.filter_by(username=username).first():
        flash('Username already exists.', 'warning')
        return redirect(url_for('main.admin_dashboard'))
    
    # Create User
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password_hash=hashed_password, is_admin=is_admin)
    
    db.session.add(new_user)
    log_action('CREATE_USER', f'Admin {current_user.username} created user {username} (Admin: {is_admin})', current_user)
    db.session.commit()
    
    flash(f'User {username} created successfully.', 'success')
    return redirect(url_for('main.admin_dashboard'))

@bp.route('/admin/user/<int:user_id>/block', methods=['POST'])
@login_required
@admin_required
def block_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('Cannot block an admin.', 'warning')
        return redirect(url_for('main.admin_dashboard'))
        
    user.is_blocked = True
    log_action('BLOCK_USER', f'User {user.username} blocked by {current_user.username}')
    db.session.commit()
    flash(f'User {user.username} has been blocked.', 'success')
    return redirect(url_for('main.admin_dashboard'))

@bp.route('/admin/user/<int:user_id>/unblock', methods=['POST'])
@login_required
@admin_required
def unblock_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_blocked = False
    log_action('UNBLOCK_USER', f'User {user.username} unblocked by {current_user.username}')
    db.session.commit()
    flash(f'User {user.username} has been unblocked.', 'success')
    return redirect(url_for('main.admin_dashboard'))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'files[]' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.url)
    
    files = request.files.getlist('files[]')
    is_public = request.form.get('is_public') == 'true'
    is_encrypted_form = request.form.get('is_encrypted') == 'true'
    encryption_data_list = request.form.getlist('encryption_data[]')
    

            
    for i, file in enumerate(files):
        if file.filename == '':
            continue
            
        if file and allowed_file(file.filename):
            # Use improved unicode-safe function
            original_filename = secure_filename_unicode(file.filename)
            
            # If filename becomes empty (e.g. all special chars), fallback to timestamp
            if not original_filename:
                original_filename = "unnamed_file"

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{timestamp}_{original_filename}"
            
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            
            try:
                # Check if file with same name exists in same folder for this user
                folder_id = request.form.get('folder_id', type=int)
                existing_file = File.query.filter_by(
                    user_id=current_user.id, 
                    folder_id=folder_id, 
                    original_name=original_filename
                ).first()

                file.save(file_path)
                enc_data = encryption_data_list[i] if i < len(encryption_data_list) else None

                if existing_file:
                    # Versioning Logic
                    from app.models import FileVersion
                    
                    # 1. Archive current state to versions
                    version = FileVersion(
                        file_id=existing_file.id,
                        filename=existing_file.filename,
                        size=existing_file.size,
                        upload_time=existing_file.upload_time,
                        version_number=existing_file.current_version,
                        is_encrypted=existing_file.is_encrypted,
                        encryption_data=existing_file.encryption_data
                    )
                    db.session.add(version)

                    # 2. Update existing file record
                    existing_file.filename = filename # New physical file
                    existing_file.size = os.path.getsize(file_path)
                    existing_file.upload_time = datetime.utcnow()
                    existing_file.current_version += 1
                    existing_file.is_encrypted = is_encrypted_form
                    existing_file.encryption_data = enc_data
                    
                    log_action('UPLOAD_VERSION', f'User {current_user.username} uploaded version {existing_file.current_version} of {original_filename}', current_user)
                    flash(f'Uploaded new version (v{existing_file.current_version}) of {original_filename}!', 'success')

                else:
                    # New File Logic
                    new_file = File(
                        filename=filename,
                        original_name=original_filename,
                        file_type=original_filename.rsplit('.', 1)[1].lower(),
                        size=os.path.getsize(file_path),
                        user_id=current_user.id,
                        is_public=is_public,
                        folder_id=folder_id,
                        is_encrypted=is_encrypted_form,
                        encryption_data=enc_data,
                        current_version=1
                    )
                    db.session.add(new_file)
                    log_action('UPLOAD', f'User {current_user.username} uploaded {original_filename} (Public: {is_public})', current_user)
                    flash(f'File {original_filename} uploaded successfully!', 'success')
                
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                flash(f'Error uploading {original_filename}: {str(e)}', 'danger')
        else:
            flash(f'File type not allowed: {file.filename}', 'warning')

    return redirect(url_for('main.dashboard'))

@bp.route('/create_folder', methods=['POST'])
@login_required
def create_folder():
    name = request.form.get('name')
    parent_id = request.form.get('parent_id', type=int) # Nullable
    
    if not name:
        flash('Folder name is required.', 'danger')
        return redirect(url_for('main.dashboard', folder_id=parent_id if parent_id else None))
        
    # Check duplicate
    if Folder.query.filter_by(user_id=current_user.id, parent_id=parent_id, name=name).first():
        flash('Folder with this name already exists.', 'warning')
        return redirect(url_for('main.dashboard', folder_id=parent_id if parent_id else None))

    is_public = request.form.get('is_public') == 'on'

    folder = Folder(name=name, user_id=current_user.id, parent_id=parent_id, is_public=is_public)
    db.session.add(folder)
    log_action('CREATE_FOLDER', f'User {current_user.username} created folder {name} (Public: {is_public})', current_user)
    db.session.commit()
    
    flash(f'Folder "{name}" created.', 'success')
    return redirect(url_for('main.dashboard', folder_id=parent_id if parent_id else None))

@bp.route('/file/<int:file_id>/share', methods=['POST'])
@login_required
def share_file(file_id):
    file = File.query.get_or_404(file_id)
    if file.owner != current_user:
        flash('You can only share files you own.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    username = request.form.get('username')
    user_to_share_with = User.query.filter_by(username=username).first()
    
    if not user_to_share_with:
        flash(f'User {username} not found.', 'warning')
        return redirect(url_for('main.dashboard'))
    
    if user_to_share_with == current_user:
         flash('You cannot share a file with yourself.', 'warning')
         return redirect(url_for('main.dashboard'))

    if user_to_share_with not in file.shared_with:
        file.shared_with.append(user_to_share_with)
        log_action('SHARE', f'User {current_user.username} shared {file.original_name} with {username}', current_user)
        db.session.commit()
        flash(f'File shared with {username}.', 'success')
    else:
        flash(f'File already shared with {username}.', 'info')
        
    return redirect(url_for('main.dashboard'))

@bp.route('/download/<int:file_id>')
@login_required
def download_file(file_id):
    file_record = File.query.get_or_404(file_id)
    
    # Check permissions: Public OR Owner OR Shared With User OR Admin
    is_shared = current_user in file_record.shared_with
    if not file_record.is_public and file_record.owner != current_user and not is_shared and not current_user.is_admin:
        abort(403)
    
    # Increment download count
    file_record.download_count += 1
    db.session.commit()

    return send_from_directory(current_app.config['UPLOAD_FOLDER'], 
                             file_record.filename, 
                             as_attachment=True,
                             download_name=file_record.original_name)

@bp.route('/view/<int:file_id>')
@login_required
def view_file(file_id):
    file_record = File.query.get_or_404(file_id)
    
    # Check permissions (same as download)
    is_shared = current_user in file_record.shared_with
    if not file_record.is_public and file_record.owner != current_user and not is_shared and not current_user.is_admin:
        abort(403)
    
    # Send inline for preview
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], 
                             file_record.filename, 
                             as_attachment=False)

@bp.route('/delete/<int:file_id>', methods=['POST'])
@login_required
def delete_file(file_id):
    file_record = File.query.get_or_404(file_id)
    
    # Only owner or admin can delete
    if file_record.owner != current_user and not current_user.is_admin:
        abort(403)
    
    try:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_record.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            
        db.session.delete(file_record)
        db.session.commit()
        flash('File deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting file: {str(e)}', 'danger')
        
    return redirect(url_for('main.dashboard'))



# --- File Versioning Routes ---

@bp.route('/file/<int:file_id>/history')
@login_required
def file_history(file_id):
    file = File.query.get_or_404(file_id)
    if file.owner != current_user and not current_user.is_admin:
        abort(403)
        
    history = []
    # Current version
    history.append({
        'version': file.current_version,
        'date': file.upload_time.strftime('%Y-%m-%d %H:%M'),
        'size': f"{round(file.size / 1024 / 1024, 2)} MB",
        'is_current': True,
        'id': 'current'
    })
    
    # Past versions
    for v in file.versions:
        history.append({
            'version': v.version_number,
            'date': v.upload_time.strftime('%Y-%m-%d %H:%M'),
            'size': f"{round(v.size / 1024 / 1024, 2)} MB",
            'is_current': False,
            'id': v.id
        })
        
    # Sort by version desc
    history.sort(key=lambda x: x['version'], reverse=True)
    
    return {'history': history, 'filename': file.original_name}

@bp.route('/file/<int:file_id>/restore/<int:version_id>', methods=['POST'])
@login_required
def restore_version(file_id, version_id):
    file = File.query.get_or_404(file_id)
    if file.owner != current_user and not current_user.is_admin:
        abort(403)
        
    from app.models import FileVersion
    version_to_restore = FileVersion.query.get_or_404(version_id)
    
    if version_to_restore.file_id != file.id:
        abort(400)
        
    try:
        # 1. Archive CURRENT state as a new version (so we don't lose it)
        # Note: We give it the current_version number, assuming we are moving forward
        # Ideally, "Restore" brings back old content but is a NEW event.
        # But to keep it simple: "Swap" logic is tricky. 
        # Better approach: "Promote" old version to be the new HEAD.
        
        # Archive what is currently the "head"
        archive_head = FileVersion(
            file_id=file.id,
            filename=file.filename,
            size=file.size,
            upload_time=file.upload_time,
            version_number=file.current_version,
            is_encrypted=file.is_encrypted,
            encryption_data=file.encryption_data
        )
        db.session.add(archive_head)
        
        # 2. Update File record to match the restored version
        # We KEEP the physical file of the version_to_restore where it is, 
        # just point the File record to it? 
        # NO, multiple records pointing to same physical file is risky if one is deleted.
        # Copying the file is safer but consumes space. 
        # UNIQUE CONSTRAINT: physical filenames are unique.
        
        # STRATEGY: Copy the restored version's file to a NEW timestamped file
        # to ensure it's treated as a fresh "upload" of that content.
        
        src_path = os.path.join(current_app.config['UPLOAD_FOLDER'], version_to_restore.filename)
        
        # Generate new name for the restored active file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        # Extract extension from original name to be safe
        ext = file.original_name.rsplit('.', 1)[1].lower() if '.' in file.original_name else 'bin'
        new_active_filename = f"{timestamp}_RESTORED_{file.original_name}" # simplified name logic
        
        dst_path = os.path.join(current_app.config['UPLOAD_FOLDER'], new_active_filename)
        
        import shutil
        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
        else:
            flash('Error: Original file for this version is missing from disk.', 'danger')
            return redirect(url_for('main.dashboard'))

        # Update File Record
        file.filename = new_active_filename
        file.size = version_to_restore.size
        # file.upload_time = datetime.utcnow() # Update time to now? Yes, it's a new "edit"
        file.upload_time = datetime.utcnow()
        file.current_version += 1
        file.is_encrypted = version_to_restore.is_encrypted
        file.encryption_data = version_to_restore.encryption_data
        
        log_action('RESTORE_VERSION', f'User {current_user.username} restored version {version_to_restore.version_number} of {file.original_name}', current_user)
        
        db.session.commit()
        flash(f'Restored version {version_to_restore.version_number} successfully.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error restoring version: {str(e)}', 'danger')

    return redirect(url_for('main.dashboard'))

# --- Profile Routes ---

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_app.config.get('OMNI_EDITION') == 'CORE':
        abort(404) # Profile not available in Core
    if request.method == 'POST':
        # Update text fields
        current_user.display_name = request.form.get('display_name')
        current_user.bio = request.form.get('bio')
        
        # Handle Avatar Upload
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename != '' and allowed_file(file.filename):
                # Secure and unique filename for avatar
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"avatar_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
                
                avatar_path = os.path.join(current_app.config['AVATAR_UPLOAD_FOLDER'], filename)
                
                try:
                    # Save new avatar
                    # (Optional: Delete old avatar if not default)
                    file.save(avatar_path)
                    current_user.avatar_file = filename
                except Exception as e:
                    flash(f'Error saving avatar: {str(e)}', 'danger')
        
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')
            
        return redirect(url_for('main.profile'))
        
    return render_template('profile.html')

@bp.route('/avatars/<filename>')
def avatar(filename):
    return send_from_directory(current_app.config['AVATAR_UPLOAD_FOLDER'], filename)
