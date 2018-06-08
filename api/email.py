from flask import current_app
import requests

def compile_message(message_array):
    return '\n'.join(m for m in message_array)

def send_application_response(recipient,subject,message_array):
    details = compile_message(message_array)
    message = 'This is an automated response message with the following information:\n{}'.format(details)

    return requests.post(
        current_app.config['MAILGUN_SUBSCRIBE_URL'],
        auth=("api", current_app.config['MAILGUN_API_KEY']),
        data={"from": current_app.config['MAILGUN_SUBSCRIBE_ADDRESS'],
              "to": recipient,
              "subject": subject,
              "text": message
            }
        )

def forward_contact_message(info):
    message_array = [
        'The WRMOTA Contact Page has received a new message from:',
        '{}\n'.format(info['address']),
        'Message:',
        info['message']
    ]
    message = compile_message(message_array)

    print('EMAIL: forwarding message from {}'.format(info['address']))
    return requests.post(
        current_app.config['MAILGUN_SUBSCRIBE_URL'],
        auth=("api", current_app.config['MAILGUN_API_KEY']),
        data={"from": current_app.config['MAILGUN_SUBSCRIBE_ADDRESS'],
              "to": current_app.config['MAILGUN_PERSONAL_ADDRESS'],
              "subject": 'New Message for WRMOTA',
              "text": message
            }
        )

def add_list_member(info):
    print('EMAIL: adding {} to list'.format(info['address']))
    return requests.post(
        current_app.config['MAILGUN_SUBSCRIBE_LIST_URL'],
        auth=('api', current_app.config['MAILGUN_API_KEY']),
        data={
            'upsert': True,
            'subscribed': info['subscribe'],
            'address': info['address'],
            'vars': '{"app":"wrmota.org","date":"'+info['date']+'","source":"site"}'
        })
