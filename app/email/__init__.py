from flask import current_app

import requests


def send_email(to, subject, body):
    config = current_app.config
    url = config['MAILGUN_API_URL'] + '/messages'
    auth = ('api', config['MAIL_GUN_API_KEY'])
    data = {'from': config['EMAIL_FROM'],
            'to': to,
            'subject': subject,
            'text': body}
    send = requests.post(url, auth=auth, data=data)

    return send
