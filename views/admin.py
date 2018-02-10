from pprint import pprint
import sqlite3
from flask import render_template, session, abort, redirect, url_for, request, flash, current_app

from wrmota.api import forms as Forms
from wrmota.api import login as Login
from wrmota import database as Database

from wrmota.views import _admin

TEMPLATE = {}

@_admin.before_request
def restrict_to_admins():
    if current_app.config['ENVIRONMENT'] == 'PRODUCTION':
        TEMPLATE['analytics'] = True
    else:
        TEMPLATE['analytics'] = False

@_admin.route('/login', methods=['GET', 'POST'])
def login():
    form = Forms.LoginUserForm()
    TEMPLATE['form'] = form

    if form.validate_on_submit():
        user = request.form['username']
        password = request.form['password']

        isUser = Database.login(user,password)
        if isUser['valid']:
            session['user'] = user
            session['token'] = isUser['token']

            flash('logged in as <b>{}</b>'.format(user))
            return redirect(url_for('_admin.index'))
    elif request.method == 'POST':
        flash('incorrect credentials')

    if 'token' in session and 'user' in session:
        flash('already logged in as <b>{}</b>. <a href="{}">log out?</a>'.format(session['user'],url_for('_admin.logout')))
    return render_template('admin/users/login.html', template=TEMPLATE)

@_admin.route('/logout')
def logout():
    del session['user']
    del session['token']
    flash('logged out')
    return redirect(url_for('_admin.login'))


@Login.requires_permission_0
def create_user():
    form = Forms.CreateUserForm()
    TEMPLATE['form'] = form
    return render_template('admin/users/create.html', template=TEMPLATE)

@_admin.route('/user/<func>', methods=['GET'])
def user_functions(func):
    if func == 'create':
        return create_user()
    else:
        return abort(404)

@_admin.route('/')
@Login.requires_permission_10
def index():
    return render_template('admin/index.html', template=TEMPLATE)

@_admin.route('/map')
@Login.requires_permission_10
def google_map():
    TEMPLATE['maps_api'] = current_app.config['GOOGLE_MAPS_API']

    map_points = Database.get_map_points()
    TEMPLATE['tables'] = {
        'address': Database.get_dict_of(map_points,name='address',json=False)
    }

    return render_template('admin/googlemaps.html', template=TEMPLATE)

@_admin.route('/data')
@Login.requires_permission_10
def all_tables():
    TEMPLATE['tables'] = {}
    data = Database.get_all_data()

    for table in data:
        t = data[table]
        TEMPLATE['tables'][t['name']] = Database.get_dict_of(t['data'],name=t['name'],json=False)

    return render_template('admin/data.html',template=TEMPLATE)
