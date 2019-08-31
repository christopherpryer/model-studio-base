# TODO: abstract & create API utilization
import functools
from flask import (Blueprint, flash, g, redirect, render_template,
request, session, url_for, current_app)
from flask_login import current_user
from werkzeug.security import check_password_hash, generate_password_hash

from . import db
from .models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(id=user_id).first()

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

def role_required(role):
    def wrapper(fn):
        @functools.wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
               return current_app.login_manager.unauthorized()
            if not current_user.has_role(role):
                return current_app.login_manager.unauthorized()
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

@bp.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=('GET', 'POST'))
@role_required('Admin')
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        error = None

        if not email:
            error = 'email is required.'
        elif not password:
            error = 'Password is required.'
        elif User.query.filter_by(email=email).first():
            error = 'email already exists.'

        if error is None:
            user = User(email=email, password=password, role=role)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('main.home'))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None
        user = User.query.filter_by(email=email).first()

        if user is None:
            error = 'Incorrect email.'
        elif not check_password_hash(user.password_hash, password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('main.home'))

        flash(error)

    return render_template('auth/login.html')

@bp.route('/reset-password', methods=('GET', 'POST'))
@login_required
def reset_password():
    if request.method == 'POST':
        password = request.form['password']
        validation = request.form['validation']
        user_id = session.get('user_id')
        user = User.query.filter_by(id=user_id).first()
        error = None

        if password is None:
            error = 'Password required.'
        elif validation is None:
            error = 'Validate password.'
        elif password != validation:
            error = 'Password does not match.'

        if error is None:
            user.password = password
            db.session.commit()
            return redirect(url_for('main.home'))

        flash(error)

    return render_template('auth/reset_password.html')
