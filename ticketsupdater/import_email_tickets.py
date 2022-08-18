from dataclasses import replace
from tabnanny import check
from django.http import HttpResponse
from django.contrib.auth.models import User
from ticketapp.models import *
import time
import sched
import email
import imaplib
import os

# helpdesk@gokhanmasterspacejv.co.ke  info@tdbsoft.co.ke
EMAIL = 'helpdesk@gokhanmasterspacejv.co.ke'
PASSWORD = 'Legal123!@#'  # Legal123!@# Netflix201501$!!
# 'imap.gmail.com' outlook.office365.com mail.tdbsoft.co.ke
SERVER = 'outlook.office365.com'


def import_email():
    try:
        print('getting tickets...')
        # connect to the server and go to its inbox
        mail = imaplib.IMAP4_SSL(SERVER)
        mail.login(EMAIL, PASSWORD)
        # we choose the inbox but you can select others
        mail.select('inbox')

        # we'll search using the ALL criteria to retrieve
        # every message inside the inbox
        # it will return with its status and a list of ids
        status, data = mail.search(None, '(UNSEEN)')
        # the list returned is a list of bytes separated
        # by white spaces on this format: [b'1 2 3', b'4 5 6']
        # so, to separate it first we create an empty list
        mail_ids = []
        attachments = MediaFiles()
        # then we go through the list splitting its blocks
        # of bytes and appending to the mail_ids list
        for block in data:
            # the split function called without parameter
            # transforms the text or bytes into a list using
            # as separator the white spaces:
            # b'1 2 3'.split() => [b'1', b'2', b'3']
            mail_ids += block.split()

        # now for every id we'll fetch the email
        # to extract its content
        for i in mail_ids:
            # the fetch function fetch the email given its id
            # and format that you want the message to be
            status, data = mail.fetch(i, '(RFC822)')

            # the content data at the '(RFC822)' format comes on
            # a list with a tuple with header, content, and the closing
            # byte b')'
            for response_part in data:
                # so if its a tuple...
                if isinstance(response_part, tuple):
                    # we go for the content at its second element
                    # skipping the header at the first and the closing
                    # at the third
                    message = email.message_from_bytes(response_part[1])
                    # with the content we can extract the info about
                    # who sent the message and its subject
                    mail_from = message['from']
                    mail_to = message['to']
                    mail_subject = message['subject']
                    # then for the text we have a little more work to do
                    # because it can be in plain text or multipart
                    # if its not plain text we need to separate the message
                    # from its annexes to get the text
                    if message.is_multipart():
                        mail_content = ''

                        # on multipart we have the text message and
                        # another things like annex, and html version
                        # of the message, in that case we loop through
                        # the email payload
                        for part in message.get_payload():
                            # if the content type is text/plain
                            # we extract it
                            if part.get_content_type() == 'text/plain':
                                mail_content += part.get_payload()
                    else:
                        # if the message isn't multipart, just extract it
                        mail_content = message.get_payload()
                    mail_content.replace(
                        '.', '.<br/>').replace(',', ',<br/>').replace(':', ':<br/>')
                    print(f'From: {mail_from}')
                    print(f'To: {mail_to}')
                    print(f'Subject: {mail_subject}')
                    print(f'Content: {mail_content}')
                    if ',' in str(mail_to):
                        assign_to, created = User.objects.get_or_create(
                            username=str(mail_to).split(',')[0].split(' ')[0], first_name=str(mail_to).split(',')[0].split(' ')[0], last_name=str(mail_to).split(',')[0].split(' ')[1], email=str(mail_to).split(',')[0].split('<')[1].strip('>'), password='@User1234')
                    elif '<' in str(mail_to):
                        assign_to, created = User.objects.get_or_create(
                            username=str(mail_to).split('<')[0].split(' ')[0], first_name=str(mail_to).split('<')[0].split(' ')[0], last_name=str(mail_to).split('<')[0].split(' ')[1], email=str(mail_to).split('<')[1].strip('>'), password='@User1234')
                    else:
                        assign_to, created = User.objects.get_or_create(
                            username=str(mail_to).strip(), email=str(mail_to).strip(), password='@User1234')
                    assign_to.is_staff = True
                    assign_to.save()
                    ticket, created = Ticket.objects.get_or_create(
                        title=str(mail_subject).strip('RE:'), issue_description=mail_content, customer_full_name=str(mail_from).split('<')[0], customer_email=str(mail_from).split('<')[1].strip('>'), assigned_to=assign_to)
                    # get attachments
                    paths = save_attachment(message)
                    if paths:
                        for path in paths:
                            attch, created = ticket.mediafiles_set.get_or_create(
                                file=path)
                    ticket.save()
                    print(ticket)
        print('done!')
    except Exception as e:
        print(e)


def save_attachment(msg, download_folder="media\\attachments"):
    try:
        att_path = "No attachment found."
        paths = []
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()
            att_path = os.path.join(download_folder, filename)

            if not os.path.isfile(att_path):
                fp = open(att_path, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()
                print('attachment downloaded')
                paths.append(att_path.strip())
            print("Paths=>{}".format(paths))
        return paths
    except Exception as e:
        print(e)
# Keep checking inbox after every 5 seconds
# s = sched.scheduler(time.time, time.sleep)
# def ckeck_mail(sc):
#     print("Checking mail...")
#     import_email()
#     print("Done!")
#     sc.enter(5, 1, ckeck_mail, (sc,))
# s.enter(5, 1, ckeck_mail, (s,))
# s.run()


# while True:
#     print("Checking mail...")
#     import_email()
#     print("Done...!")
#     print("-----------------------")
#     print("waiting for 30 secs...")
#     time.sleep(30)
