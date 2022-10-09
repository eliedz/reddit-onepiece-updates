import sys
import os
import yaml
import praw
import prawcore
import re
import smtplib
from email.mime.text import MIMEText

# Google libraries
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from email.message import EmailMessage


SCOPES = ['https://www.googleapis.com/auth/gmail.send']


# scraper imports
import requests
from bs4 import BeautifulSoup

def google_auth():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

creds = google_auth()

def send_mail(title, url, spoiler):

    service = build('gmail', 'v1', credentials=creds)

    FROM = config['email']['sender_address']
    text = title + " is out! Check it out at " + url + "\n"
    if not spoiler:
        text += '~!~EXPERIMENTAL~!~ \nThe manga URL should be: ' + scrape_url()
        TO = config['email']['chapter_recipients']
    else:
        TO = config['email']['spoiler_recipients']


    msg = EmailMessage()
    msg.set_content(text)
    msg['To'] = ",".join(TO)
    print(msg['To'])
    msg['From'] = FROM
    msg['Subject'] = title + " is out!!!"

    encoded_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    create_message = {
        'raw': encoded_message
    }
    # pylint: disable=E1101
    send_message = (service.users().messages().send
                    (userId="me", body=create_message).execute())
    print(F'Message Id: {send_message["id"]}')


def scrape_url():
    source = requests.get("https://onepiecechapters.com/mangas/5/one-piece").content
    soup = BeautifulSoup(source, features="html.parser")
    url = soup.find('a', href=True, attrs={'class': 'block border border-border bg-card mb-3 p-3 rounded'})['href']
    return 'https://onepiecechapters.com' + url

config = yaml.safe_load(open(sys.argv[1]))

reddit = praw.Reddit(
    client_id=config['reddit_api']['client_id'],
    client_secret=config['reddit_api']['client_secret'],
    user_agent=config['reddit_api']['user_agent'],
)

for i in range(1,3):
    try:
        stickies = reddit.subreddit("onepiece").sticky(i)
    except prawcore.exceptions.NotFound:
        break
    ss_title = stickies.title
    ss_url = stickies.url

    # Flairs are too unpredicatably applied/used to work for this consistently
    if re.match('.*chapter 1[0-9]{3} spoilers.*', ss_title, re.IGNORECASE):

        with open(config['nb_files']['spoiler'], "r") as f:
            ch_nb = int(f.readlines()[0])
        ss_nb = int(re.search('1[0-9]{3}',ss_title).group(0))

        if ss_nb >= ch_nb:
            ss_nb = ss_nb + 1
            with open(config['nb_files']['spoiler'], "w") as f:
                f.write(str(ss_nb))
            send_mail(ss_title, ss_url, True)

    elif re.match('one piece: chapter 1[0-9]{3}$', ss_title, re.IGNORECASE):
        with open(config['nb_files']['chapter'], "r") as f:
            ch_nb = int(f.readlines()[0])
        ss_nb = int(re.search('1[0-9]{3}',ss_title).group(0))

        if ss_nb >= ch_nb:
            ss_nb = ss_nb + 1
            with open(config['nb_files']['chapter'], "w") as f:
                f.write(str(ss_nb))
            send_mail(ss_title, ss_url, False)
