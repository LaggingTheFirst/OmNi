import os

class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-this-in-prod'
    
    # Database
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'omni.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Uploads
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    AVATAR_UPLOAD_FOLDER = os.path.join(basedir, 'uploads', 'avatars')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 * 1024  # 16 GB max file size
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'rar', 'mp4', 'mp3', 'mkv', 'iso', 'exe', 'msi'}
    
    # Admin (Default credentials, change these!)
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'admin' 
    
    # Network
    HOST = '0.0.0.0'
    PORT = 5000

    @staticmethod
    def init_app(app):
        if not os.path.exists(Config.UPLOAD_FOLDER):
            os.makedirs(Config.UPLOAD_FOLDER)
        if not os.path.exists(Config.AVATAR_UPLOAD_FOLDER):
            os.makedirs(Config.AVATAR_UPLOAD_FOLDER)
        
        # Ensure instance folder exists for SQLite db
        instance_path = os.path.join(Config.basedir, 'instance')
        if not os.path.exists(instance_path):
            os.makedirs(instance_path)
