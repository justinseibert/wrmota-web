from functools import wraps
from flask import abort, session, g, url_for, redirect

from wrmota import database as Database

def check_login_status(level):
    if not hasattr(g, 'permission'):
        print('g.permission does yet exist')
        try:
            g.permission = Database.get_session_permission(session['token'])
        except:
            return False
    if g.permission <= level:
        return True

def requires_permission_10(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        permission = check_login_status(10)
        if not permission:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function

def requires_permission_5(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        permission = check_login_status(5)
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
