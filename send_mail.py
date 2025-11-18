'''
This module sends emails with attachments to the participants
Reference - https://developers.google.com/gmail/api/quickstart/python

In order to run this module, you need to enable Gmail API and download client_secrets.json file
'''

from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import mimetypes
import os
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
import base64
import cv2


# If modifying these scopes, delete the file token.json.
# We are using Gmail API to send emails
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def aunthentication():
    creds = None
    
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        # Load the credentials from the file
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        # Refresh the token if it has expired
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # If there are no valid credentials available, let the user log in.
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def prepare_and_send_email(sender, recipient, subject, message_text, im0= None):
    """Prepares and send email with attachment to the participants 

    Args:
        sender: Email address of the sender.
        recipient: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.
        im0: The image to be attached 
    
    Returns:
        None
    """
    # Get credentials 
    creds = aunthentication()

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)

        #create message using a custo, function create_message()
        msg = create_message(sender, recipient, subject, message_text, im0)
        # send the message using a custom function send_message()
        send_message(service, 'me', msg) #here 'me' is the user_id of the authenticated user

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


def create_message(sender, to, subject, message_text, img_file=None):
    """Create a message for an email."""

    # ---------------------------------------
    # CASE 1: No image provided -> send text only
    # ---------------------------------------
    if img_file is None:
        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject

        return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

    # ---------------------------------------
    # CASE 2: Image exists -> send attachment
    # ---------------------------------------
    message = MIMEMultipart()
    message['from'] = sender
    message['to'] = to
    message['subject'] = subject

    # create directory
    base_loc = 'static/violations/'
    if not os.path.exists(base_loc):
        os.makedirs(base_loc)

    location = 'GRIL Office'
    current_date_time = time.time()
    formatted_date_time = time.strftime("%H:%M:%S_%d-%m-%Y", time.localtime(current_date_time))
    file_name = base_loc + 'violation_' + location + '_' + formatted_date_time + '.jpg'

    # save image
    cv2.imencode('.jpg', img_file)[1].tofile(file_name)

    # attach text
    message.attach(MIMEText(message_text))

    # attach image
    with open(file_name, 'rb') as f:
        img_data = f.read()
        img = MIMEImage(img_data)
        img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_name))
        message.attach(img)

    return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}



def send_message(service, user_id, message):
    """Send an email message.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.

    Returns:
        Sent Message.
    """
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                    .execute())
        print('Message Id: %s' % message['id'])
        return message
    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    
    # Uncomment the following lines to run the code locally
    # set sender and recipient accordingly
    # sender must be a gmail account using which you have enabled the gmail API
    prepare_and_send_email(sender='harshitkeshari9621@gmail.com', 
                           recipient='har1998shit@gmail.com',
                           subject= 'Hi Automated Mail', 
                           message_text= 'Hi How Are You ??'
    )
    pass
    
    
