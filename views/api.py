from datetime import datetime
from uuid import uuid4
from flask import jsonify, abort, request, current_app, session, render_template
import requests
from pprint import pprint

from wrmota.api import _api
from wrmota.api import forms as Forms
from wrmota.api import hashes as Hash
from wrmota.api import login as Login
from wrmota.api import sanitize as Sanitize
from wrmota import database as Database

@_api.route('/create_user', methods=['POST'])
@Login.requires_permission(0)
def create_user():
    data = {
        'error': False,
        'message': 'default message'
    }
    form = Forms.CreateUserForm()
    if form.validate_on_submit():
        user = request.form
        Database.add_curator(user)
        data['errors'] = False
        data['message'] = 'User "{}" successfully created.'.format(request.form['username'])
    else:
        data['errors'] = form.errors
        data['message'] = 'There was an error with your form.'

    return jsonify(data)

def update_artist_data():
    response = {}
    form = Forms.EditArtistForm()
    form.curator.choices = Forms.get_curators()
    if form.validate_on_submit():
        update = Database.update_artist_data(form)
        if update:
            response['errors'] = False
            response['message'] = 'Artist "{}" successfully updated.'.format(request.form['artist'])
        else:
            response = Forms.handle_error(form)
    else:
        response = Forms.handle_error(form)

    return response

@_api.route('/edit/<data>', methods=['POST'])
@Login.requires_permission(5)
def api_edit_data(data):
    if data == 'artist':
        response = update_artist_data()
    else:
        response = {
            'error': False,
            'message': 'default message'
        }
    return jsonify(response)

def extract_audio_from_email(email,attachments):
    message = 'EMAIL: unable to extract audio from {}'.format(email['from'])
    status = 406
    verify = False

    try:
        message = 'EMAIL: routing verified from {}'.format(email['from'])
        status = 200

        code = Sanitize.code(email['subject'])
        count = int(email['attachment-count'])

        # if code and count > 0:
        #     file_saved = Forms.handle_upload(attachments, field='attachment-', extension='audio')
        #     for i in range(1,count+1):
        #         id = 'attachment-{}'.format(i)
        #         file = request.files[id]

        # import os
        # from werkzeug.utils import secure_filename
        # filename = secure_filename(f.filename)
        #     location = os.path.join(current_app.config['TEMP_UPLOAD_FOLDER'], filename)
        # print(location)
        # f.save(location)
    except:
        return message, 406

    print(message)
    return message, status

@_api.route('/test-upload')

@_api.route('/accept-email/<data>', methods=['POST'])
def accept_email_data(data):
    verified = Hash.verify_email(current_app.config['MAILGUN_API_KEY'], request.form)

    if verified and data == 'recording':
        response = extract_audio_from_email(request.form,request.files)
    else:
        response = 'EMAIL ROUTE: invalid url', 406
    return response

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
