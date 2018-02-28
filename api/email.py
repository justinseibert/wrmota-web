from flask import current_app
import requests

def send_application_response(recipient,subject,message_array):
    details = '\n'.join(m for m in message_array)
    message = "Hello!\n\n This is an automated response message with the following information:\n\n {}".format(details)

    return requests.post(
        current_app.config['MAILGUN_API_URL'],
        auth=("api", current_app.config['MAILGUN_API_KEY']),
        data={"from": current_app.config['MAILGUN_SUBSCRIBE_ADDRESS'],
              "to": recipient,
              "subject": subject,
              "text": message
            }
        )
