from functools import wraps
from flask import abort, session, g, url_for, redirect, request

from wrmota import database as Database

def check_login_status(level):
    if not hasattr(g, 'permission'):
        print('Getting user...')
        try:
            g.permission = Database.get_session_permission(session['token'])
        except:
            print('ERROR: no user')
            return None

    print('USER: '+g.user)
    if g.permission <= level:
        return True
    else:
        print('ERROR: invalid permission for ' + request.path)
        return False

def requires_permission(level):
    def permission_decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            permission = check_login_status(level)
            if permission == True:
                return func(*args, **kwargs)
            elif permission == None:
                return redirect(url_for('_admin.login'))
            elif permission == False:
                return abort(403)
        return func_wrapper
    return permission_decorator
