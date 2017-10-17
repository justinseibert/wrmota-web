import sqlite3
from flask import render_template, session, abort, redirect, url_for, request, flash

from wrmota.api import forms as Forms
from wrmota import database as Database

from wrmota.views import _admin

@_admin.before_request
def restrict_to_admins():
    if 'logged_in' not in session:
        session['logged_in'] = False

    if not session['logged_in'] and request.path != '/login':
        abort(403)

@_admin.route('/')
def index():
    return render_template('admin/index.html')

@_admin.route('/login', methods=['GET', 'POST'])
def login():
    form = Forms.LoginForm()
    if form.validate_on_submit():
        session['logged_in'] = True
        flash('logged in')
        return redirect(url_for('_admin.index'))
    elif request.method == 'POST':
        flash('incorrect credentials')

    return render_template('admin/login.html', form=form)

@_admin.route('/logout')
def logout():
    session['logged_in'] = False
    flash('logged out')
    return redirect(url_for('_admin.login'))
