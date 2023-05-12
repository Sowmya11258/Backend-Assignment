import mysql.connector
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# set up MySQL connection
cnx = mysql.connector.connect(user='root', password='',
                              host='localhost',
                              database='admin')
cursor = cnx.cursor()

# set up Gmail API client
creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/gmail.modify'])
service = build('gmail', 'v1', credentials=creds)

# retrieve list of messages
messages = service.users().messages().list(userId='me').execute()

# loop through messages and insert them into database
for message in messages['messages']:
    message_data = service.users().messages().get(userId='me', id=message['id']).execute()
    headers = message_data['payload']['headers']
    subject = ''
    sender = ''
    date = ''
    body = ''
    for header in headers:
        if header['name'] == 'Subject':
            subject = header['value']
        if header['name'] == 'From':
            sender = header['value']
        if header['name'] == 'Date':
            date = header['value']
    if 'payload' in message_data and 'body' in message_data['payload']:
        body_data = message_data['payload']['body']
        if 'data' in body_data:
            body = body_data['data']
            # process the body data here
        else:
            # handle the case when the 'data' key is missing
            pass

    # insert email data into MySQL database
    add_message = ("INSERT INTO emails "
                   "(subject, sender, date, body) "
                   "VALUES (%s, %s, %s, %s)")
    data_message = (subject, sender, date, body)
    cursor.execute(add_message, data_message)
    cnx.commit()

# close MySQL connection
cursor.close()
cnx.close()