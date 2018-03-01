import sqlite3
from pprint import pprint
from flask import render_template, abort, current_app, redirect, url_for

from wrmota.api import forms as Forms
from wrmota import database as Database
from wrmota.views import _site

TEMPLATE = {}

@_site.before_request
def check_environment():
    if current_app.config['ENVIRONMENT'] == 'PRODUCTION':
        TEMPLATE['analytics'] = True
    else:
        TEMPLATE['analytics'] = False

@_site.route('/')
def index():
    TEMPLATE['email'] = Forms.EmailForm()
    return render_template('site/index.html', template=TEMPLATE)

@_site.route('/login')
def admin_login():
    return redirect(url_for('_admin.login'))

@_site.route('/lookup')
def admin_lookup():
    return redirect(url_for('_admin.code_lookup_for_emails'))

@_site.route('/artists')
def artists():
    artists = Database.get_artists_involved()
    TEMPLATE['artists'] = {
        'visitor' : Database.get_dict_of(artists['visitor'], name='visitor'),
        'local' : Database.get_dict_of(artists['local'], name='local'),
    }
    TEMPLATE['options'] = {
        'tilt' : ['rotate1','rotate-1', '', '', '', '']
    }
    return render_template('site/artists.html', template=TEMPLATE)
