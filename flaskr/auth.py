import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

# Create authentication Blueprint to organize views and code related to auth
bp = Blueprint('auth', __name__, url_prefix='/auth')

# Registration route and view
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        # Confirm user provided inputs
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        # Try creating the new user
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                # Need to use commit() after hashing pw
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))
        # flash() stores the error message for use in template
        flash(error)

    return render_template('auth/register.html')

# Login route and view
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
        
        if user is None:
            error = 'Incorrect username.'
        # Compare submitted pw by hashing and comparing to stored, hashed pw
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        
        if error is None:
            # session is a dict and stored in a cookie
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        
        flash(error)

    return render_template('auth/login.html')

# Validate users using the cookie before all requests
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id)
        ).fetchone()

# Log out route and view
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# To secure views requiring login, create a decorator
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            # Prepend the BP before the view name (function name)
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view