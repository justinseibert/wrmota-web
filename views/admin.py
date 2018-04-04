from pprint import pprint
import sqlite3
from itertools import product
from random import shuffle, choice
from flask import render_template, session, abort, redirect, url_for, request, flash, current_app

from wrmota.api import forms as Forms
from wrmota.api import login as Login
from wrmota.api import sanitize as Sanitize
from wrmota import database as Database

from wrmota.views import _admin

TEMPLATE = {}

@_admin.before_request
def restrict_to_admins():
    # return abort(503)
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
        else:
            flash('Unable to log in')
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

@Login.requires_permission(0)
def create_user():
    form = Forms.CreateUserForm()
    TEMPLATE['form'] = form
    return render_template('admin/users/create.html', template=TEMPLATE)

@_admin.route('/user/<func>', methods=['GET'])
@Login.requires_permission(5)
def user_functions(func):
    if func == 'create':
        return create_user()
    else:
        return abort(404)

@_admin.route('/')
@Login.requires_permission(10)
def index():
    return render_template('admin/index.html', template=TEMPLATE)

@Login.requires_permission(5)
def view_all_tables():
    TEMPLATE['tables'] = {}
    data = Database.get_all_data()

    for table in data:
        t = data[table]
        TEMPLATE['tables'][t['name']] = Database.get_dict_of(t['data'],name=t['name'],json=False)

    return render_template('admin/view/data.html',template=TEMPLATE)

@Login.requires_permission(10)
def view_address_codes():
    TEMPLATE['tables'] = {}
    codes = Database.get_address_codes()

    TEMPLATE['tables']['codes'] = Database.get_dict_of(codes, name='codes', json=False)
    return render_template('admin/view/address-codes.html',template=TEMPLATE)

@Login.requires_permission(10)
def view_google_map():
    # TEMPLATE['maps_api'] = current_app.config['GOOGLE_MAPS_API']
    #
    # map_points = Database.get_dict_of(Database.get_map_points(), name='address')
    # for p in map_points['data']:
    #     p['brick'] = Sanitize.brick_as_letter(p['brick'])
    #
    # TEMPLATE['tables'] = {
    # 'address': map_points
    # }

    return render_template('admin/view/googlemaps.html', template=TEMPLATE)

@Login.requires_permission(10)
def view_print_map_data():
    paper = Database.get_dict_of(Database.get_print_map_data(), name='paper')
    for p in paper['data']:
        p['brick'] = Sanitize.brick_as_letter(p['brick'])
        p['visitor'] = Sanitize.visitor_status(p['visitor'])
        p['story'] = '' if p['story'] == None else p['story']

    TEMPLATE['tables'] = {
        'paper': paper
    }

    return render_template('admin/view/print-map-data.html', template=TEMPLATE)

@_admin.route('/view/<data>')
@Login.requires_permission(10)
def view_data(data):
    if data == 'data':
        return view_all_tables()
    elif data == 'codes':
        return view_address_codes()
    elif data == 'map':
        return view_google_map()
    elif data == 'paper':
        return view_print_map_data()
    else:
        return abort(404)

@Login.requires_permission(5)
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
    return render_template('admin/task/edit_artist.html', template=TEMPLATE)

@Login.requires_permission(5)
def send_artist_emails():
    curators = Database.get_curators_list()
    curator_options = {
        'none': 'no',
        'all': 'all'
    }
    for curator in curators:
        curator_options[curator] = "{}'s".format(curator)
    TEMPLATE['curators'] = curator_options

    filter_options = {
        'none': 'no filter',
        'confirmed': 'confirmed',
        'visitor': 'visitor',
        'touched_base': 'touched base',
        'art_received': 'art received',
    }
    TEMPLATE['options'] = filter_options

    data = Database.get_dict_of(Database.get_data_artist(), name='artist')
    TEMPLATE['artist'] = data

    cols = ['id','artist','curator','art_received','visitor','confirmed','touched_base','email']
    TEMPLATE['tables'] = {
        'artist' : Database.keep_cols_in_dict(data,cols)
    }

    return render_template('admin/task/send_email.html', template=TEMPLATE)

@Login.requires_permission(10)
def print_color_codes():
    codes = Database.get_address_codes()
    TEMPLATE['codes'] = Database.get_dict_of(codes)
    return render_template('admin/task/print-colors.html', template=TEMPLATE)

@_admin.route('/task/<data>')
@Login.requires_permission(10)
def edit_data(data):
    if data == 'artists':
        return edit_artist_data()
    elif data == 'email':
        return send_artist_emails()
    elif data == 'print-codes':
        return print_color_codes()
    else:
        return abort(404)

@_admin.route('/lookup')
def code_lookup_for_emails():
    TEMPLATE['tables'] = {}
    codes = Database.get_address_codes()

    codes = Database.get_dict_of(codes, name='codes', json=False)
    for c in codes['data']:
        uploaded_by = Sanitize.email_sender(c['uploaded by'])
        c['brick'] = Sanitize.brick_as_letter(c['brick'])
        c['uploaded by'] = uploaded_by['name'] if uploaded_by else c['uploaded by']
    TEMPLATE['tables']['codes'] = codes
    return render_template('admin/task/find-codes.html',template=TEMPLATE)

@_admin.route('/test')
@Login.requires_permission(0)
def test_update():
    return abort(404)
    # return Sanitize.email_sender('Justin Seibert <justin@wrmota.org>')['email']
