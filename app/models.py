from datetime import datetime
from app.extensions import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Association table for file sharing
file_shares = db.Table('file_shares',
    db.Column('file_id', db.Integer, db.ForeignKey('file.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

# Association table for folder sharing
folder_shares = db.Table('folder_shares',
    db.Column('folder_id', db.Integer, db.ForeignKey('folder.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=None)
    
    # Profile Fields
    display_name = db.Column(db.String(50), nullable=True) # Optional display name
    bio = db.Column(db.String(500), nullable=True)         # Short bio
    avatar_file = db.Column(db.String(20), nullable=False, default='default.png') # Avatar filename
    
    files = db.relationship('File', backref='owner', lazy=True, cascade="all, delete-orphan")
    shared_files = db.relationship('File', secondary=file_shares, backref=db.backref('shared_with', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return f"User('{self.username}', 'Admin: {self.is_admin}')"

class Folder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=True) # For subfolders
    is_public = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref='folders', lazy=True)
    parent = db.relationship('Folder', remote_side=[id], backref='subfolders', lazy=True)
    files = db.relationship('File', backref='folder', lazy=True, cascade="all, delete-orphan")
    
    shared_with = db.relationship('User', secondary=folder_shares, backref=db.backref('shared_folders', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return f"Folder('{self.name}')"

    def __repr__(self):
        return f"Folder('{self.name}')"

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False) # Stored secure filename
    original_name = db.Column(db.String(255), nullable=False) # Display name
    file_type = db.Column(db.String(50), nullable=False)
    size = db.Column(db.Integer, nullable=False) # bytes
    upload_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    download_count = db.Column(db.Integer, default=0)
    is_public = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=True) # Nullable for root

    def __repr__(self):
        return f"File('{self.filename}', '{self.size} bytes', 'Public: {self.is_public}')"

    is_encrypted = db.Column(db.Boolean, default=False)
    encryption_data = db.Column(db.Text, nullable=True) # JSON string storing IV and Salt
    current_version = db.Column(db.Integer, default=1)
    versions = db.relationship('FileVersion', backref='file', lazy=True, cascade="all, delete-orphan")

class FileVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False) # Physical filename of this version
    size = db.Column(db.Integer, nullable=False)
    upload_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    version_number = db.Column(db.Integer, nullable=False)
    
    # Metadata snapshot (crucial for encrypted files)
    is_encrypted = db.Column(db.Boolean, default=False)
    encryption_data = db.Column(db.Text, nullable=True) 

    def __repr__(self):
        return f"FileVersion('{self.version_number}', '{self.filename}')"

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Nullable for system logs or anon
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.String(500))
    user = db.relationship('User', backref='logs', lazy=True)

    def __repr__(self):
        return f"Log('{self.timestamp}', '{self.action}')"
