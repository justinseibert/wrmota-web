from datetime import datetime
from uuid import uuid4
from flask import jsonify, abort, request, current_app, session, render_template
import requests

from wrmota.api import forms as Forms
from wrmota.api import _api

@_api.route('/subscribe', methods=['POST'])
def email_subscribe():
    validform = Forms.EmailForm()
    if validform.validate_on_submit():
        info = {
            'address' : request.form['email'],
            'date' : get_formatted_datetime(),
            'subscribe': True
        }

        add_list_member(info)

        data = {
            'errors': False,
            'from': current_app.config['MAILGUN_SUBSCRIBE_ADDRESS']
        }
    else:
        data = {
            'errors': True,
            'data' : validform.errors
        }
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
