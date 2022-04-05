import sys
import yaml
import praw
import prawcore
import re
import smtplib
from email.mime.text import MIMEText

# scraper imports
import requests
from bs4 import BeautifulSoup

def send_mail(title, url, spoiler):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(config['email']['sender_address'], config['email']['sender_password'])

    FROM = config['email']['sender_address']
    text = title + " is out! Check it out at " + url + "\n"
    if not spoiler:
        text += '~!~EXPERIMENTAL~!~ \nThe manga URL should be: ' + scrape_url()
        TO = config['email']['chapter_recipients']
    else:
        TO = config['email']['spoiler_recipients']


    msg = MIMEText(text)
    msg['To'] = ",".join(TO)
    msg['From'] = FROM
    msg['Subject'] = title + " is out!!!"

    server.sendmail(FROM, TO, msg.as_string())

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
