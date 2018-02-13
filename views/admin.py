from pprint import pprint
import sqlite3
from itertools import product
from random import shuffle, choice
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
@Login.requires_permission_5
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
@Login.requires_permission_5
def all_tables():
    TEMPLATE['tables'] = {}
    data = Database.get_all_data()

    for table in data:
        t = data[table]
        TEMPLATE['tables'][t['name']] = Database.get_dict_of(t['data'],name=t['name'],json=False)

    return render_template('admin/data.html',template=TEMPLATE)

@_admin.route('/permutation/<combo>')
@Login.requires_permission_10
def permutation(combo):
    TEMPLATE['permutation'] = []

    if combo == '4x4':
        iter = product('ABCD',repeat=4)
        skip = 2
        add = False
    elif combo == '5x3':
        iter = product('ABCDE',repeat=3)
        skip = 1
        add = True
    else:
        abort(404)

    i = 0
    for j in iter:
        if (i/skip) <= 110:
            if add:
                k = list(j)
                k.append(choice('ABCDE'))
                j = k[::-1]
            TEMPLATE['permutation'].append(j)
        i += skip
    return render_template('admin/permutation.html', template=TEMPLATE)

@Login.requires_permission_5
def edit_artist_data():
    data = Database.get_dict_of(Database.get_data_artist(), name='artist')
    TEMPLATE['artist'] = data
    cols = ['id','artist','curator','art_received']
    TEMPLATE['tables'] = {
        'artist' : Database.keep_cols_in_dict(data,cols)
    }

    form = Forms.EditArtistForm()
    form.curator.choices = Forms.get_curators()
    TEMPLATE['form'] = form
    return render_template('admin/edit/artist.html', template=TEMPLATE)

@_admin.route('/edit/<data>')
@Login.requires_permission_10
def edit_data(data):
    if data == 'artists':
        return edit_artist_data()
