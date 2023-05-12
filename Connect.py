import mysql.connector
from datetime import datetime, timezone
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from retrive import authenticate


class Database:
    def _init_(self):
        self.db = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='gmail_db'
        )
        self.cursor = self.db.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id INT PRIMARY KEY AUTO_INCREMENT,
                thread_id VARCHAR(255),
                subject VARCHAR(255),
                sender VARCHAR(255),
                recipient VARCHAR(255),
                message VARCHAR(1000),
                received_date DATETIME
            )
        """)

    def insert_email(self, thread_id, subject, sender, recipient, message, received_date):
        sql = "INSERT INTO emails (thread_id, subject, sender, recipient, message, received_date) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (thread_id, subject, sender, recipient, message, received_date)
        self.cursor.execute(sql, val)
        self.db.commit()


def fetch_emails():
    try:
        service = authenticate()
        results = service.users().messages().list(userId='me', maxResults=10).execute()
        messages = results.get('messages', [])

        if not messages:
            print('No messages found.')
        else:
            db = Database()
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                thread_id = msg['threadId']
                subject = ''
                sender = ''
                recipient = ''
                message_body = ''

                headers = msg['payload']['headers']
                for header in headers:
                    if header['name'] == 'Subject':
                        subject = header['value']
                    elif header['name'] == 'From':
                        sender = header['value']
                    elif header['name'] == 'To':
                        recipient = header['value']

                if 'parts' in msg['payload']:
                    for part in msg['payload']['parts']:
                        if part['mimeType'] == 'text/plain':
                            message_body = part['body']['data']
                            break
                else:
                    message_body = msg['payload']['body']['data']

                received_date = datetime.fromtimestamp(int(msg['internalDate']) / 1000, timezone.utc)

                db.insert_email(thread_id, subject, sender, recipient, message_body, received_date)

            print('Messages successfully stored in the database.')

    except HttpError as error:
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    fetch_emails()