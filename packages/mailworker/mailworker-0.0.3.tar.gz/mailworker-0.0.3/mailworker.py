#!/usr/bin/env python
# encoding: utf-8
"""
mail_worker.py

# GNU General Public Licence (GPL)
# 
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA
"""
__all__ = ['mailworker']
__version__ = '0.0.3'

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from hotqueue import HotQueue
from logbook import Logger

mail_queue = HotQueue("mail_queue", host="localhost", port=6379, db=0)

def create_email(message, username=None, password=None, server=None):
    try:
        assert message, username, password, server

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = message['subject']
        msg['From'] = message['from']
        msg['To'] = message['to']

        # Create the body of the message (a plain-text and an HTML version).
        # text is your plain-text email
        # html is your html version of the email
        # if the reciever is able to view html emails then only the html
        # email will be displayed
        text = "Hi!\nHow are you?\n"
        html = """\
        <html>
          <head></head>
          <body>
            <p>Thanks for your interest in Precision Stock.<br>
               Please feel free to 
            </p>
          </body>
        </html>
        """
        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        # Attach parts into message container.
        msg.attach(part1)
        msg.attach(part2)
        # Open a connection to the SendGrid mail server
        s = smtplib.SMTP('smtp.sendgrid.net', 587)
        # Authenticate
        s.login(username, password)
        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        s.sendmail(message['from'],  message['to'], msg.as_string())
        s.quit()
    except (AssertionError, Exception):
        log.error('Invalid message - required field missing: %s' % message.keys())
        raise
    

def process_messages():
    events_queue = HotQueue("mail_queue", host="localhost", port=6379, db=0)
    for message in mail_queue.consume():
        log.info('Processing mail for %s' % message)
        create_email(message)
        
if __name__ == '__main__':
    log = Logger(__name__)
    log.info('Waiting for mail messages to process...')
    process_messages()
