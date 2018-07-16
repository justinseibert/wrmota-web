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
    TEMPLATE['mapPage'] = 0
    TEMPLATE['title'] = None
    TEMPLATE['description'] = None

@_site.route('/')
def index():
    return render_template('site/index.html', template=TEMPLATE)

@_site.route('/map')
def map():
    TEMPLATE['title'] = 'Map'
    TEMPLATE['description'] = "Find the location of every artwork in our current exhibit. View artist information and read a breif preview of the local story."
    TEMPLATE['mapPage'] = 1
    return render_template('site/map.html', template=TEMPLATE)

@_site.route('/artists')
def artists():
    TEMPLATE['title'] = 'Artists'
    artists = Database.get_artists_involved()
    TEMPLATE['artists'] = {
    'visitor' : Database.get_dict_of(artists['visitor'], name='visitor'),
    'local' : Database.get_dict_of(artists['local'], name='local'),
    }
    TEMPLATE['options'] = {
    'tilt' : ['rotate1','rotate-1', '', '', '', '']
    }
    TEMPLATE['description'] = "A list of over 100 local and visiting artists participating in WRMOTA's current exhibit."
    return render_template('site/artists.html', template=TEMPLATE)

@_site.route('/credits')
def credits():
    TEMPLATE['title'] = 'Credits'
    TEMPLATE['description'] = "Learn about the hard working people that made WRMOTA possible."
    return render_template('site/credits.html', template=TEMPLATE)

@_site.route('/privacy')
def privacy():
    TEMPLATE['title'] = 'Privacy Policy'
    return render_template('site/privacy.html', template=TEMPLATE)

@_site.route('/contact')
def contact():
    TEMPLATE['title'] = 'Contact'
    TEMPLATE['description'] = "Sign up for our newsletter to learn about upcoming events. Contact us for more information."
    TEMPLATE['email'] = Forms.EmailForm()
    return render_template('site/contact.html', template=TEMPLATE)

@_site.route('/news/<data>')
def newsletter(data):
    TEMPLATE['title'] = 'WRMOTA: News {}'.format(data)
    TEMPLATE['include_analytics'] = True
    newsletter = 'email/{}.html'.format(data)
    return render_template(newsletter, template=TEMPLATE)

@_site.route('/login')
def admin_login():
    return redirect(url_for('_admin.login'))

@_site.route('/logout')
def admin_logout():
    return redirect(url_for('_admin.logout'))
