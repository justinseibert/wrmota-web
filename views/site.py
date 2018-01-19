import sqlite3
from flask import render_template, abort

from wrmota.api import forms as Forms
from wrmota.api import data as Data
from wrmota.views import _site

@_site.route('/')
def index():
    email = Forms.EmailForm()
    return render_template('site/index.html', email=email)

@_site.route('/artists')
def artists():
    file = 'static/site/data/artists.csv'
    artists = Data.CSVdata(file).as_dict('confirmed')
    options = {
        'tilt' : ['rotate1','rotate-1', '', '', '', '']
    }
    return render_template('site/artists.html', artists=artists, options=options)
