import sqlite3
from flask import render_template, abort

from wrmota.api import forms as Forms
from wrmota.views import _site

@_site.route('/')
def index():
    email = Forms.EmailForm()
    return render_template('site/index.html', email=email)
