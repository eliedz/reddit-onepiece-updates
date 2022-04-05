# One Piece Subreddit polling bot

This script polls r/OnePiece waiting for the spoiler and chapter announcements.
Once those are found it sends an email to the interested parties notifying them.

## Quickstart

### Python dependencies
Test and working on `python3.8`, however it should still work on previous or 
later versions of Python3.

#### Install required packages
From the root of the repository
```
pip3 install -r requirements.txt
```

### Config
The script expects a filename passed as a command line argument which points to
a yaml file containing all of the necessary configuration. An example config
can be found in [example_var.yaml](example_var.yaml). You'll need to provide
your own email credentials as well as Reddit API credentials in the
corresponding variables.
A custom list of email addresses to notify can also be added with seperate lists
for emails to notify when a spoiler vs a chapter is out, in case some people do
not care to see early spoilers.

### Example Usage
From the root of the repository
```
python3 morgans.py example_var.yaml
```
