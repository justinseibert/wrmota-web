from pprint import pprint
import sqlite3
from flask import render_template, session, abort, redirect, url_for, request, flash, current_app

from wrmota.api import forms as Forms
from wrmota import database as Database

from wrmota.views import _admin

TEMPLATE = {}

@_admin.before_request
def restrict_to_admins():
    if current_app.config['ENVIRONMENT'] == 'PRODUCTION':
        TEMPLATE['analytics'] = True
    else:
        TEMPLATE['analytics'] = False

    if 'logged_in' not in session:
        session['logged_in'] = False
        session['user'] = ''
    if not session['logged_in'] and request.path != url_for('_admin.login'):
        print(request.path)
        return redirect(url_for('_admin.login'))

@_admin.route('/login', methods=['GET', 'POST'])
def login():
    form = Forms.LoginForm()
    if form.validate_on_submit():
        session['logged_in'] = True
        session['user'] = form['username'].data

        flash('logged in as <b>{}</b>'.format(session['user']))
        return redirect(url_for('_admin.index'))
    elif request.method == 'POST':
        flash('incorrect credentials')

    if session['logged_in']:
        flash('already logged in as <b>{}</b>. <a href="{}">log out?</a>'.format(session['user'],url_for('_admin.logout')))
    return render_template('admin/login.html', form=form, template=TEMPLATE)

@_admin.route('/logout')
def logout():
    session['logged_in'] = False
    flash('logged out')
    return redirect(url_for('_admin.login'))

@_admin.route('/')
def index():
    return render_template('admin/index.html', template=TEMPLATE)

@_admin.route('/map')
def google_map():
    TEMPLATE['maps_api'] = current_app.config['GOOGLE_MAPS_API']

    map_points = Database.get_map_points()
    TEMPLATE['tables'] = {
        'address': Database.get_dict_of(map_points,name='address',json=False)
    }

    return render_template('admin/googlemaps.html', template=TEMPLATE)

@_admin.route('/data')
def all_tables():
    db = Database.get_db()
    tables = [
        'address',
        'artist',
        'media',
        'address_meta',
        'artist_meta',
        'media_meta',
    ]
    template = {
        'tables': {}
    }
    for table in tables:
        statement = "SELECT * FROM {}".format(table)
        data = db.execute(statement).fetchall()
        template['tables'][table] = {
            'head' : data[0].keys(),
            'data' : data,
        }
    return render_template('admin/data.html',template=TEMPLATE)
