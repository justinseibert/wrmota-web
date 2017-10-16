import sqlite3
from flask import render_template, abort

from wrmota import database as Database

from wrmota.views import _site

@_site.route('/')
def index():
    return render_template('site/index.html')
