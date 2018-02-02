import sqlite3
from flask import render_template, session, abort, redirect, url_for, request, flash, current_app

from wrmota.api import forms as Forms
from wrmota import database as Database

from wrmota.views import _admin

@_admin.before_request
def restrict_to_admins():
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
    return render_template('admin/login.html', form=form)

@_admin.route('/logout')
def logout():
    session['logged_in'] = False
    flash('logged out')
    return redirect(url_for('_admin.login'))

@_admin.route('/')
def index():
    return render_template('admin/index.html')

@_admin.route('/map')
def google_map():
    maps_api = current_app.config['GOOGLE_MAPS_API']
    return render_template('admin/edit-data.html', maps_api=maps_api)

@_admin.route('/measure')
def measure():
    return render_template('admin/measure.html')

@_admin.route('/multiple')
def multiple():
    return render_template('admin/multiple.html')

@_admin.route('/map2')
def map():
    return render_template('admin/map.html')

@_admin.route('/data')
def data():
    db = Database.get_db()
    tables = [
        'address',
        'media',
        'artist'
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
    return render_template('admin/data.html',template=template)
