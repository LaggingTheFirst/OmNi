from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app.extensions import bcrypt
from app.utils import log_action

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Normalize
        if username:
            username = username.lower()
        
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            if user.is_blocked:
                flash('Your account has been blocked. Please contact the administrator.', 'danger')
                return render_template('login.html')
                
            login_user(user)
            
            # Log login
            # Log login
            log_action('LOGIN', f'User {user.username} logged in', user)
            
            return redirect(url_for('main.dashboard'))
            
        flash('Login Unsuccessful. Please check username and password', 'danger')
            
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
