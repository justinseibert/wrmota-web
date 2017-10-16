import sqlite3
from flask import render_template, abort

from wrmota import database as Database

from wrmota.views import _admin

@_admin.route('/')
def index():
    return render_template('admin/index.html')
