import imaplib
import email
from email.header import decode_header
import webbrowser
import os

# account credentials
username = "helpdesk@gokhanmasterspacejv.co.ke"
password = "Legal123!@#"
# use your email provider's IMAP server, you can look for your provider's IMAP server on Google
# or check this page: https://www.systoolsgroup.com/imap/
# for office 365, it's this:
imap_server = "outlook.office365.com"


# Connect securely with SSL
imap = imaplib.IMAP4_SSL(imap_server)

# Login to remote server
imap.login(username, password)

imap.select('Inbox')

tmp, messages = imap.search(None, 'ALL')
for num in messages[0].split():
    # Retrieve email message by ID
    tmp, data = imap.fetch(num, '(RFC822)')
    msg = data[0][1]
    print('From: {0}\nTo:{1}'.format(msg[0], msg[1], msg[2]))
    break
imap.close()
imap.logout()
