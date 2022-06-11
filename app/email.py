import boto3
from botocore.exceptions import ClientError
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import json
import requests

def send_email(subject, sender, recipients, text_body, html_body):
    SENDER = sender
    RECIPIENT = recipients
    CONFIGURATION_SET = ""
    CHARSET = "UTF-8"
    AWS_REGION = "ap-south-1"
    SUBJECT = subject
    BODY_TEXT =text_body
    BODY_HTML = html_body
    client = boto3.client('ses',region_name=AWS_REGION)
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            ConfigurationSetName=CONFIGURATION_SET,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])

# def send_grid_mail(subject, sender, recipients, text_body, html_body):
#     message = Mail(
#         from_email='NOLE Mailer <mailer@nole.ai>',
#         to_emails=recipients,
#         subject=subject,
#         html_content=html_body)
#     try:
#         print(os.environ.get('SENDGRID_API_KEY'))
#         sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
#         response = sg.send(message)
#         print(response.status_code)
#         print(response.body)
#         print(response.headers)
#     except Exception as e:
#         print(e)

def send_grid_mail(subject, sender, recipients, text_body, html_body):
    sender_email = "mailer@nole.ai"  # Your website's official email address
    api_key = os.environ.get('SENDGRID_API_KEY')

    if sender_email and api_key:
        url = "https://api.sendgrid.com/v3/mail/send"

        data = {"personalizations": [{
            "to": [{"email": recipients}],
            "subject": subject
        }],

            "from": {
                "email": sender_email,
                'name': "NOLE Mailer"
            },

            "content": [{
                "type": "text/html",
                "value": html_body
            }]

        }

        headers = {
            'authorization': "Bearer {0}".format(api_key),
            'content-type': "application/json"
        }
        try:
            response = requests.request("POST", url=url, data=json.dumps(data), headers=headers)
            print("Sent to SendGrid")
            print(response.text)
            return True
        except Exception as e:
            print(e)
            return False
    else:
        print("No env vars or no email address")

def send_confirmation_email(confirmation_id, email, name):
    base_url = app.config['BASE_URL']
    data = {
        "template_id": "d-335db9b46c12429eae2b7a662752ea07",
        "from": {
            "email": "no-reply@neurodex.app",
            "name": "Neurodex"
        },
        "personalizations": [{
            "to": [
                {
                    "email": email,
                    "name": name
                }
            ],
            "dynamic_template_data": {
                "confirmationLink": f"{base_url}/confirm-email/{confirmation_id}",
                "name": name
            }
        }]
    }
    return sg.client.mail.send.post(request_body=data)