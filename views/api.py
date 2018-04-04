from datetime import datetime
from uuid import uuid4
from flask import jsonify, abort, request, current_app, session, render_template, redirect, url_for
from flask_cors import CORS, cross_origin
import requests
from pprint import pprint

from wrmota.api import _api
from wrmota.api import forms as Forms
from wrmota.api import hashes as Hash
from wrmota.api import login as Login
from wrmota.api import email as Email
from wrmota.api import provide as Provide
from wrmota.api import update as Update
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

def extract_audio_from_email():
    email = request.form
    audio = request.files

    has_code = Sanitize.is_code(email['subject'])
    sender = email['from']
    notes = Sanitize.make_unicode(email['subject'])
    body = Sanitize.make_unicode(email['stripped-text'])
    story = Sanitize.remove_email_confidentiality_statement(body)

    message = []

    if 'attachment-count' in email and email['attachment-count'] > 0:
        file_saved = Forms.handle_upload(audio, 'audio')
        uploaded = file_saved['uploads']
        failed = file_saved['failed']

        if len(uploaded) > 0:
            new_media = []
            for upload in uploaded:
                new_media.append((
                    upload['directory'],
                    upload['name'],
                    upload['filetype'],
                    upload['extension'],
                    None,
                    upload['original_filename'],
                    notes,
                    story,
                    sender
                ))

            added_files = ', '.join(u['original_filename'] for u in uploaded)
            if Database.add_media(new_media):
                message.append("SUCCESS: uploaded {}".format(added_files))
                if has_code:
                    link_message = Database.set_audio_per_code(uploaded[0]['name'],has_code)
                    message.append(link_message)
                else:
                    message.append("ERROR: no 4-letter code was found in the subject line")
            else:
                message.append("ERROR: unable to add {} to database".format(added_files))

        if len(failed) > 0:
            failed_files = ', '.join(f for f in failed)
            message.append("ERROR: unable to upload {}".format(failed_files))
    else:
        message.append("ERROR: no attachments were found")

    message_allowed_files = ', '.join(i for i in current_app.config['ALLOWED_FILES']['audio'])
    message.append('''
    \n------------\n
    Please Note:
    - Messages should be sent to recordings@wrmota.org from your students.wyoarea.org email address
    - The email upload system only supports these filetypes: {}.
    - To link you new file with the correct address you must specify the 4-letter address code in the Subject Line of your email. Codes can be found here: https://wrmota.org/admin/lookup
    - You can add any notes or descriptions for the file in the Body of your email.
    - If you are having other issues, please contact Justin: justin@wrmota.org
    '''.format(message_allowed_files))
    Email.send_application_response(sender, 'Your Audio Uploads', message)

    return 'Message accepted', 200

@_api.route('/accept-email/<data>', methods=['POST'])
# see app level for CSRF exemption
@cross_origin()
def accept_email_data(data):
    verified = Hash.verify_mail_origin(current_app.config['MAILGUN_API_KEY'], request.form)

    if verified and data == 'recording':
        response = extract_audio_from_email()
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

@_api.route('/v1/get/<data>')
# see app level for CSRF exemption
@cross_origin()
def get_json_data(data):
    if data == 'all':
        return Provide.all_data()
    elif data == 'map':
        return Provide.map_data()
    elif data == 'test':
        return 'success', 200
    else:
        return abort(400)

@_api.route('/v1/post/<option>', methods=['POST'])
@Login.requires_permission(5)
def post_json_data(option):
    if option == 'latLng':
        data = request.get_json();
        return Update.latLng(data)
    else:
        return abort(400)

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
