import os
from flask import Flask
from config import Config
from app.extensions import db, bcrypt, login_manager
from app.setup_handlers import ensure_app_structure

def create_app(config_class=Config):
    # 1. Run the setup handler FIRST to ensure folders/config exist in AppData
    app_data_path = ensure_app_structure()

    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 2. Load the persistent config from the AppData location if it exists
    config_file = os.path.join(app_data_path, 'config.py')
    if os.path.exists(config_file):
        app.config.from_pyfile(config_file)

    # CRITICAL: Force paths to AppData to ensure persistence in .exe mode
    # This overrides any relative-path defaults from source config that might point to _MEIPASS
    app.config['UPLOAD_FOLDER'] = os.path.join(app_data_path, 'uploads')
    app.config['AVATAR_UPLOAD_FOLDER'] = os.path.join(app_data_path, 'uploads', 'avatars')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app_data_path, 'instance', 'omni.db').replace('\\', '/')

    # Ensure these specific persistent folders exist (just in case)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['AVATAR_UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')), exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    
    # Initialize Config logic (create upload dirs etc)
    config_class.init_app(app)

    # Register Blueprints / Routes
    from app import routes, auth
    app.register_blueprint(routes.bp)
    app.register_blueprint(auth.bp, url_prefix='/auth')

    # Edition Context Processor
    @app.context_processor
    def inject_edition():
        return dict(
            OMNI_EDITION=app.config.get('OMNI_EDITION', 'CORE'),
            IS_CORE=app.config.get('OMNI_EDITION') == 'CORE',
            IS_NEXUS=app.config.get('OMNI_EDITION') == 'NEXUS'
        )

    with app.app_context():
        db.create_all()
        check_db_schema(db)
        create_default_admin(app, db, bcrypt)

    return app

def create_default_admin(app, db, bcrypt):
    from app.models import User
    admin_user = User.query.filter_by(username=app.config['ADMIN_USERNAME']).first()
    if not admin_user:
        hashed_password = bcrypt.generate_password_hash(app.config['ADMIN_PASSWORD']).decode('utf-8')
        admin = User(username=app.config['ADMIN_USERNAME'], password_hash=hashed_password, is_admin=True)
        db.session.add(admin)
        db.session.commit()

def check_db_schema(db):
    """Simple check to add missing columns to existing databases without full migrations."""
    import sqlite3
    from flask import current_app
    
    db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    if not os.path.isabs(db_path):
        db_path = os.path.join(current_app.instance_path, db_path)
    
    # ...
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check folder_shares table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='folder_shares'")
        if not cursor.fetchone():
            print("Migrating database: Creating 'folder_shares' table...")
            cursor.execute('''CREATE TABLE folder_shares (
                folder_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                PRIMARY KEY (folder_id, user_id),
                FOREIGN KEY(folder_id) REFERENCES folder (id),
                FOREIGN KEY(user_id) REFERENCES user (id)
            )''')
            conn.commit()
            
        # Check if is_public exists in folder table
        cursor.execute("PRAGMA table_info(folder)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_public' not in columns:
            print("Migrating database: Adding 'is_public' column to 'folder' table...")
            cursor.execute("ALTER TABLE folder ADD COLUMN is_public BOOLEAN DEFAULT 0")
            conn.commit()

        # Check encryption columns in file table
        cursor.execute("PRAGMA table_info(file)")
        file_columns = [column[1] for column in cursor.fetchall()]

        if 'is_encrypted' not in file_columns:
            print("Migrating database: Adding 'is_encrypted' column to 'file' table...")
            cursor.execute("ALTER TABLE file ADD COLUMN is_encrypted BOOLEAN DEFAULT 0")
        
        if 'encryption_data' not in file_columns:
            print("Migrating database: Adding 'encryption_data' column to 'file' table...")
            cursor.execute("ALTER TABLE file ADD COLUMN encryption_data TEXT")

        if 'current_version' not in file_columns:
            print("Migrating database: Adding 'current_version' column to 'file' table...")
            cursor.execute("ALTER TABLE file ADD COLUMN current_version INTEGER DEFAULT 1")
            
        # Check profile columns in user table (Phase 2)
        cursor.execute("PRAGMA table_info(user)")
        user_columns = [column[1] for column in cursor.fetchall()]
        
        if 'bio' not in user_columns:
            print("Migrating database: Adding 'bio' to 'user' table...")
            cursor.execute("ALTER TABLE user ADD COLUMN bio VARCHAR(500)")

        if 'avatar_file' not in user_columns:
            print("Migrating database: Adding 'avatar_file' to 'user' table...")
            cursor.execute("ALTER TABLE user ADD COLUMN avatar_file VARCHAR(20) DEFAULT 'default.png'")

        if 'display_name' not in user_columns:
             print("Migrating database: Adding 'display_name' to 'user' table...")
             cursor.execute("ALTER TABLE user ADD COLUMN display_name VARCHAR(50)")

        # Log database encoding for verification
        cursor.execute("PRAGMA encoding;")
        encoding = cursor.fetchone()[0]
        print(f"Database orientation: SQLite @ {db_path}")
        print(f"Database encoding: {encoding}")

        conn.commit()
            
        conn.close()
    except Exception as e:
        print(f"Schema check/migration skipped: {e}")
