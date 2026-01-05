from app.extensions import db
from app.models import Log
from flask_login import current_user

def log_action(action, details, user=None):
    if not user:
        user = current_user if current_user.is_authenticated else None
    
    log = Log(
        action=action,
        details=details,
        user_id=user.id if user else None
    )
    db.session.add(log)
    db.session.commit()
