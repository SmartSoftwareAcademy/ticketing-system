from ast import ExceptHandler
import csv
from email import message
from email.mime import image
import json
import random
import shelve
import email
import imaplib
from tokenize import group
from unicodedata import name
from django.core.mail import send_mail
from django.conf import settings
from .models import *
from .email_regex import GetEmailDetails
import os
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.sites.models import Site
from django.utils import timezone
from django.conf import settings
import re
from django.core.mail.backends.smtp import EmailBackend
from django.contrib import messages
from django.contrib.auth.models import User, Group


class EmailDownload:

    """This Class Downloads emails in the inbox of a particular gmail account and create a csv file with the information"""

    #################################################################################################################################
    def __init__(self,request, email, password):
        """Yeah, initializing everything"""
        self.email = str(email)
        self.password = str(password)
        self.request=request
        print('Checking mail...')
        try:
            #default admin
            df_admin, created = User.objects.get_or_create(username="superadmin", email="info@tdbsoft.co.ke", password="@Admin123") 
            df_admin.is_superuser = True
            df_admin.is_staff = True
            df_admin.save()
            user_groups= Group.objects.all()
            list_names = ["ExternalAdmins", "Admins", "Agents"]
            for name in list_names:
                for g in user_groups:
                    if name.lower() ==  str(g.name).lower():
                        pass
                    else:
                        group, created = Group.objects.get_or_create(name=name)
        except Exception as e:
            print("group create error:{}".format(e))
    #################################################################################################################################

    def send_email(self,subject, body, to,attachments):
        try:
            config = OutgoinEmailSettings.objects.all()[0]
            #print(imap_settings.email_id, imap_settings.email_password)
            backend = EmailBackend(host=config.email_host, port=config.email_port, username=config.support_reply_email,
                                password=config.email_password, use_tls=config.use_tls, fail_silently=config.fail_silently)
            message = re.sub(r'(?<!&nbsp;)&nbsp;', ' ',strip_tags(body))#replace &nbsp; with space
            if attachments:
                email = EmailMessage(subject=subject,body=message, from_email=config.support_reply_email, to=to, connection=backend)
                for attch in attachments:
                    #filename = str(protocol+'\\'+str(domain)+'\\'+str(attch.file))
                    #print(filename)
                    email.attach(attch.name, attch.read(),
                                    attch.content_type)
                email.send()
                messages.success(self.request, 'Email sent successfully!')
            else:
                email = EmailMessage(
                    subject=subject, body=message, from_email=config.support_reply_email, to=to, connection=backend)
                email.send()
                messages.success(self.request, 'Email sent successfully!')
        except Exception as e:
            messages.info(self.request,"Email send error:{}".format(e))
            
        
    def login_to_imap_server(self):
        """Log in to the imap server"""

        # connecting to the server
        print("Trying to connect to the server")

        try:
            imapObj = imaplib.IMAP4_SSL(
                'mail.tdbsoft.co.ke')  # outlook.office365.com
            print("Successfully connected to the IMAP server...")

            # Try logging into gmail
            print("Trying to log in to gmail...")

            try:
                imapObj.login(self.email, self.password)
                print("Logged in")
                self.select_email_uids(imapObj)
            except Exception as e:
                print(e)
                print("Failed to log you in, make sure your password and email are correct \nand that your have enabled non-google apps in the google settings")

        except:
            print("Failed to connect, probably some network error")

    #################################################################################################################################

    def select_email_uids(self, imap_object):
        """Select uids for email data to be extracted"""
        imap_object.select('INBOX')
        _, self.uids = imap_object.search(None, '(UNSEEN)')
        self.get_email_content_from_uids(imap_object)
        self.logout_of_imap_server(imap_object)

    #################################################################################################################################

    # TODO: Create a function that calls envelope with args self.uids
    def get_email_content_from_uids(self, imap_object):
        """Get email data from the respective email uid"""
        try:
            with shelve.open('data') as db:
                counter = db['counter']
        except KeyError:
            counter = 0

        if counter == 0:

            for num in self.uids[0].split():
                try:
                    _, data = imap_object.fetch(num, '(RFC822)')
                    _, bytes_data = data[0]

                    # convert the byte data to message
                    email_message = email.message_from_bytes(bytes_data)
                    # self.save_data_in_json(email_message)
                    # self.save_data_in_csv(email_message)
                    self.save_to_db(email_message)
                except Exception as e:
                    print(e)
        else:
            for num in self.uids[0].split()[counter:]:
                try:
                    _, data = imap_object.fetch(num, '(RFC822)')
                    _, bytes_data = data[0]

                    # convert the byte data to message
                    email_message = email.message_from_bytes(bytes_data)
                    #self.save_data_in_json(email_message)
                    #self.save_data_in_csv(email_message)
                    self.save_to_db(email_message)
                except Exception as e:
                    print(e)

        print("saving counter")
        with shelve.open('data') as db:
            db['counter'] = counter

    #################################################################################################################################

    def save_data_in_csv(self, email_message):
        """Writing the information to a csv file"""

        subject = email_message["subject"]
        to = email_message["to"]
        from_ = email_message["from"]
        date_ = email_message["date"]
        for part in email_message.walk():
            if part.get_content_type() == "text/plain" or part.get_content_type() == "text/html":
                message = part.get_payload(decode=True)
                message = message.decode('utf-8', 'ignore')
                break

        data_output_file = open('email_data.csv', 'a', newline='')
        csv_writer = csv.writer(data_output_file)

        csv_writer.writerow([date_, from_, to, subject, message])
        data_output_file.close()

    #################################################################################################################################

    def save_to_db(self, email_message):
        try:
            config = OutgoinEmailSettings.objects.all()[0]
            user,created=User.objects.get_or_create(username='chatbot',first_name='chatbot', last_name='chatbot', password="@User1234", is_staff=True, is_superuser=True)
            subject = email_message["subject"]
            mail_to = email_message["to"]
            mail_from_ = email_message["from"]
            date_ = email_message["date"]
            for part in email_message.walk():
                if part.get_content_type() == "text/plain" or part.get_content_type() == "text/html":
                    message = part.get_payload(decode=True)
                    message = message.decode('utf-8', 'ignore')
                    break
            #####################download attachment####################################
            att_path = "No attachment found."
            download_folder = "media\\attachments"
            paths = []
            for part in email_message.walk():
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
                ############################################################################
            email_details = GetEmailDetails(message)
            if config.support_reply_email in str(mail_to).lower():
                mail_to = str(mail_to).strip(config.support_reply_email)
                print("Mail_to:{}".format(mail_to))
                if ',' in str(mail_to):
                    assign_to, created = User.objects.get_or_create(
                    username=str(mail_to).split(',')[0].split(' ')[0].strip('\"'), first_name=str(mail_to).split(',')[0].split(' ')[0], last_name=str(mail_to).split(',')[0].split(' ')[1], email=str(mail_to).split(',')[0].split('<')[1].strip('>'), password='@User1234')
                elif '<' in str(mail_to):
                    assign_to, created = User.objects.get_or_create(
                        username=str(mail_to).split('<')[0].split(' ')[0].strip('\"'), first_name=str(mail_to).split('<')[0].split(' ')[0], last_name=str(mail_to).split('<')[0].split(' ')[1], email=str(mail_to).split('<')[1].strip('>'), password='@User1234')
                else:
                    assign_to, created = User.objects.get_or_create(
                        username=str(mail_to).strip('\"').strip(), email=str(mail_to).strip(), password='@User1234')
                assign_to.is_staff = True
                group = Group.objects.get(name="Agents")
                if assign_to not in group.user_set.all():
                    assign_to.groups.add(group)
                assign_to.save()
            else:
                assign_to = random.choice(
                    User.objects.exclude(username='chatbot').exclude(username='superadmin').exclude(email='').exclude(groups__name='ExternalAdmins'))

            # ticket_object = Ticket.objects.create(
            #     user=user,
            #     title=subject,
            #     customer_full_name=email_message['from'],
            #     customer_phone_number=email_details.get_phone_number(),
            #     customer_email=email_details.get_email(),
            #     issue_description=email_details.get_issue_description(),
            #     ticket_section=email_details.get_issue_section(),
            #     created_date=date_
            # )
            ticket, created = Ticket.objects.get_or_create(
                title=str(subject).strip('RE:'), 
                issue_description=message,
                customer_full_name=str(mail_from_).split('<')[0], 
                customer_email=str(mail_from_).split('<')[1].strip('>'), 
                ticket_section=email_details.get_issue_section(),
                customer_phone_number=email_details.get_phone_number())
            if config.auto_assign_tickets:
                ticket.assigned_to = assign_to
                to_list = [assign_to.email, ]
            else:
               to_list = [str(mail_to).strip(config.support_reply_email),]
            print(to_list)
            # get attachments            
            if paths:
                for path in paths:
                    attch, created = ticket.mediafiles_set.get_or_create(
                        file=path)
            ticket.save()
            if config.send_auto_email_on_ticket_creation:
                #send client email
                try:
                    recipient_list = [str(mail_from_).split('<')[1].strip('>'), ]
                    print("recipient_list:{}".format(recipient_list))
                    subject = 'Issue recieved'
                    message = config.code_for_automated_reply.replace(
                        '[id]', ticket.ticket_id).replace('[request_description]', ticket.issue_description).replace('[tags]','None').replace('[date]',str(timezone.now()))
                    attachments = []#ticket.mediafiles_set.all()
                    # Site.objects.get_current().domain
                    self.send_email(subject,message,recipient_list,attachments)
                except Exception as e:
                  print("customer email error:{}".format(e))
            if config.send_auto_email_on_agent_assignment:
                try:
                    # send mail to assignee
                    print("to list:{}".format(to_list))
                    domain = self.request.META['HTTP_HOST']
                    protocol = 'https' if self.request.is_secure() else 'http'
                    ticket_url = protocol+"://"+domain+'/ticket-detail/{}/'.format(ticket.id)
                    message = config.code_for_automated_assign.replace(
                        '[id]', ticket.ticket_id).replace('[request_description]', ticket.issue_description).replace('[tags]', 'None').replace('[date]', str(timezone.now())).replace('[ticket_link]', ticket_url).replace('[assignee]', ticket.assigned_to.username)
                    subject = "Ticket assignmet:(#{})".format(ticket.ticket_id)
                    print("recipient list:".format(to_list))
                    self.send_email(subject, message,
                                    to_list, attachments)
                except Exception as e:
                  print("assignee email error:{}".format(e))
            print("Ticket created successfully}")
        except Exception as e:
            print("create error:{}".format(e))

    ##################################################################################################################################

    def save_data_in_json(self, email_message):
        """Writing the information to a json file"""
        subject = email_message["subject"]
        to = email_message["to"]
        from_ = email_message["from"]
        date_ = email_message["date"]
        for part in email_message.walk():
            if part.get_content_type() == "text/plain" or part.get_content_type() == "text/html":
                message = part.get_payload(decode=True)
                message = message.decode('utf-8', 'ignore')
                break

        # 1. Convert the data into a dictionary
        email_dict = {
            "date": date_,
            "from": from_,
            "to": to,
            "subject": subject,
            "text": message,
        }

        # 2. Convert the dictionary into json then dump the shit into a json file
        with open("email_data.json", 'a') as f:
            f.write(json.dumps(email_dict, sort_keys=True,
                    indent=4))
   #################################################################################################################################

    def logout_of_imap_server(self, imap_object):
        """This function logs out of the imap server"""

        print("Logging Out...")
        imap_object.close()
        imap_object.logout()
        print("Logged Out!!")

    #################################################################################################################################