from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials


def authenticate():
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/gmail.modify'])

    service = build('gmail', 'v1', credentials=creds)

    return service


def fetch_emails():
    try:
        service = authenticate()
        result = service.users().messages().list(userId='me').execute()
        messages = result.get('messages', [])

        if not messages:
            print('No messages found.')
        else:
            print(f'Total messages: {len(messages)}')
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                print(f'Subject: {msg["payload"]["headers"][15]["value"]}')
                print(f'From: {msg["payload"]["headers"][16]["value"]}')
                print(f'To: {msg["payload"]["headers"][17]["value"]}')
                print(f'Date: {msg["payload"]["headers"][20]["value"]}')
                print('\n\n')

    except HttpError as error:
        print(f'An error occurred: {error}')
        return None


if __name__ == '__main__':
    fetch_emails()