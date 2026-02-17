import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from app.setup_handlers import get_app_data_path
from app.utils import log_action

bp = Blueprint('setup', __name__)

@bp.route('/setup', methods=['GET', 'POST'])
def index():
    if current_app.config.get('SETUP_COMPLETE', False):
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        secret_key = request.form.get('secret_key')
        admin_user = request.form.get('admin_username')
        admin_pass = request.form.get('admin_password')
        
        if not secret_key or not admin_user or not admin_pass:
            flash('All fields are required.', 'danger')
            return render_template('setup.html')
            
        # Update the AppData config.py
        app_data_path = get_app_data_path()
        config_path = os.path.join(app_data_path, 'config.py')
        
        new_config = f"""import os

# AppData Config for OmNi (Updated by Setup Wizard)

# SECURITY: Changed during setup
SECRET_KEY = {repr(secret_key)}

# Network Settings
HOST = '0.0.0.0'
PORT = 5000

# Admin Credentials (Updated during setup)
ADMIN_USERNAME = {repr(admin_user)}
ADMIN_PASSWORD = {repr(admin_pass)}

# Setup Status
SETUP_COMPLETE = True

# Database & Uploads
# Paths are automatically handled by the app.
"""
        try:
            with open(config_path, 'w') as f:
                f.write(new_config)
            
            # Update current app config
            current_app.config['SETUP_COMPLETE'] = True
            current_app.config['SECRET_KEY'] = secret_key
            current_app.config['ADMIN_USERNAME'] = admin_user
            current_app.config['ADMIN_PASSWORD'] = admin_pass

            # Sync with Database
            from app.models import User
            from app.extensions import db, bcrypt
            
            # Update existing admin or create new one
            admin = User.query.filter_by(is_admin=True).first()
            hashed_password = bcrypt.generate_password_hash(admin_pass).decode('utf-8')
            
            if admin:
                admin.username = admin_user
                admin.password_hash = hashed_password
            else:
                admin = User(username=admin_user, password_hash=hashed_password, is_admin=True)
                db.session.add(admin)
            
            db.session.commit()
            
            flash('Setup complete! Your admin account has been updated.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Error saving configuration: {e}', 'danger')
            
    return render_template('setup.html')
