from functools import wraps
from flask import abort, session

from wrmota import database as Database

def check_login_status(level):
    if 'token' not in session:
        return False
    elif 'token' in session:
        permission = Database.get_session_permission(session['token'])
        if permission <= level:
            return True
        else:
            return False

def requires_permission_10(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        permission = check_login_status(10)
        if not permission:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function

def requires_permission_0(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        permission = check_login_status(0)
        if not permission:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function
