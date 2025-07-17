from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app.models.user import User, Business
from app.utils.auth_helpers import safe_check_password_hash, safe_generate_password_hash
from app import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and safe_check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        flash('Invalid username or password', 'danger')
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')

@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        if not safe_check_password_hash(current_user.password, current_password):
            flash('Current password is incorrect', 'danger')
            return redirect(url_for('auth.change_password'))
        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return redirect(url_for('auth.change_password'))
        try:
            user = User.query.get(current_user.id)
            user.password = safe_generate_password_hash(new_password)
            db.session.commit()
            flash('Password updated successfully', 'success')
            return redirect(url_for('auth.profile'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating password: {e}', 'danger')
    return render_template('auth/change_password.html')

@bp.route('/register', methods=['POST'])
def register():
    business_name = request.form.get('business_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    gst_number = request.form.get('gst_number')
    full_name = request.form.get('full_name')
    reg_username = request.form.get('reg_username')
    reg_password = request.form.get('reg_password')
    try:
        business = Business(
            business_name=business_name,
            email=email,
            phone=phone,
            address=address,
            gst_number=gst_number
        )
        db.session.add(business)
        db.session.flush()  # Get business.id
        hashed_pw = safe_generate_password_hash(reg_password)
        user = User(
            username=reg_username,
            password=hashed_pw,
            full_name=full_name,
            email=email,
            role='admin',
            business_id=business.id
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Registration successful! Your business and user account have been registered.', 'success')
        return redirect(url_for('main.dashboard'))
    except Exception as e:
        db.session.rollback()
        flash(f'Registration failed: {e}', 'danger')
        return redirect(url_for('auth.login')) 