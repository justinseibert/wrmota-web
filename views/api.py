from datetime import datetime
from uuid import uuid4
from flask import jsonify, abort, request, current_app, session, render_template
import requests
from pprint import pprint

from wrmota.api import _api
from wrmota.api import forms as Forms
from wrmota import database as Database

@_api.route('/create_user', methods=['POST'])
def create_user():
    data = {
        'error': False,
        'message': 'default message'
    }
    form = Forms.CreateUserForm()
    if form.validate_on_submit():
        user = request.form
        Database.add_curator(user)
        # if added:
        data['errors'] = False
        data['message'] = 'User "{}" successfully created.'.format(request.form['username'])
        # else:
        #     data['errors'] = True
        #     data['message'] = 'An error occurred. Unable to create new user.'
    else:
        data['errors'] = form.errors
        data['message'] = 'There was an error with your form.'

    return jsonify(data)

# @_api.route('/check_user', methods=['POST'])
# def check_user():
#     data = {
#         'errors': True,
#         'message': 'Nope, that didn\'t work.'
#     }
#     form = Forms.LoginUserForm()
#     if form.validate_on_submit():
#         user = request.form['username']
#         password = request.form['password']
#
#         isUser = Database.login(user,password)
#
#         if isUser['valid']:
#             session['user'] = user
#             session['token'] = isUser['token']
#             data['errors'] = False
#             data['message'] = 'Successfully logged in!'
#
#     return redirect(url_for())

@_api.route('/subscribe', methods=['POST'])
def email_subscribe():
    data = {}
    validform = Forms.EmailForm()
    if validform.validate_on_submit():
        info = {
            'address' : request.form['email'],
            'date' : get_formatted_datetime(),
            'subscribe': True
        }

        add_list_member(info)

        data['errors'] = False
        data['message'] = 'Success! Be on the look out for emails from <i>{}</i>'.format(current_app.config['MAILGUN_SUBSCRIBE_ADDRESS'])
    else:
        print(validform.errors)
        data['errors'] = validform.errors
        data['message'] = 'There was an error with your form.'

    return jsonify(data)

# def send_complex_message(info):
#     return requests.post(
#         current_app.config['MAILGUN_API_URL'],
#         auth=("api", current_app.config['MAILGUN_API_KEY']),
#         data={"from": current_app.config['MAILGUN_SUBSCRIBE_ADDRESS'],
#               "to": info['address'],
#               "subject": 'Get in touch',
#               "text": "Hi! This is just a quick confirmation email showing that you've subscribed to recieve updates about WRMOTA (West Reading Museum of Temporary Art). If you did not expect this, please unsubscribe. Otherwise, no further action is required.\n\n--The WRMOTA Team\nwrmota.org",
#               "html": render_template('email/subscribe.html', title='Welcome to WRMOTA')
#             })

def add_list_member(info):
    print('adding to list')
    return requests.post(
        current_app.config['MAILGUN_SUBSCRIBE_LIST'],
        auth=('api', current_app.config['MAILGUN_API_KEY']),
        data={
            'upsert': True,
            'subscribed': info['subscribe'],
            'address': info['address'],
            'vars': '{"app":"wrmota.org","date":"'+info['date']+'","source":"site"}'
        })

def get_formatted_datetime():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
