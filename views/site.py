import sqlite3
from flask import render_template, abort, current_app, redirect, url_for

from wrmota.api import forms as Forms
from wrmota.api import data as Data
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
def login():
    return redirect(url_for('_admin.login'))

@_site.route('/artists')
def artists():
    file = 'static/site/data/artists.csv'
    TEMPLATE['artists'] = Data.CSVdata(file).as_dict('confirmed')
    TEMPLATE['options'] = {
        'tilt' : ['rotate1','rotate-1', '', '', '', '']
    }
    return render_template('site/artists.html', template=TEMPLATE)
