from email import message
from django.shortcuts import render
from django.http.response import HttpResponse
import os
import mimetypes
import datetime
from operator import concat
from django.shortcuts import redirect, render, HttpResponseRedirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.conf import settings
from .models import *
from .forms import *
from .get_email import EmailDownload
from ticketsupdater.import_email_tickets import import_email
from django.utils import timezone
import re
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail import EmailMessage
from django.utils.html import strip_tags


def send_email(request, subject, body, to, attachments):
    try:
        config = OutgoinEmailSettings.objects.all()[0]
        #print(imap_settings.email_id, imap_settings.email_password)
        backend = EmailBackend(host=config.email_host, port=config.email_port, username=config.support_reply_email,
                               password=config.email_password, use_tls=config.use_tls, fail_silently=config.fail_silently)
        # replace &nbsp; with space
        message = re.sub(r'(?<!&nbsp;)&nbsp;', ' ', strip_tags(body))
        if attachments:
            email = EmailMessage(
                subject=subject, body=message, from_email=config.support_reply_email, to=to, connection=backend)
            for attch in attachments:
                #filename = str(protocol+'\\'+str(domain)+'\\'+str(attch.file))
                # print(filename)
                email.attach(attch.name, attch.read(),
                             attch.content_type)
            email.send()
            messages.success(request, 'Email sent successfully!')
        else:
            email = EmailMessage(
                subject=subject, body=message, from_email=config.support_reply_email, to=to, connection=backend)
            email.send()
            messages.success(request, 'Email sent successfully!')
    except Exception as e:
        messages.info(request, "Email send error:{}".format(e))


def sync_tickets(request):
    import_email()
    return redirect('ticketapp:all-tickets')


class TicketListView(LoginRequiredMixin, generic.ListView):
    model = Ticket
    template_name = 'ticketapp/index.html'

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            if self.request.user.is_superuser:
                context['all_issues'] = Ticket.objects.all().count()
                context['urgent_count'] = Ticket.objects.filter(
                    ticket_priority="Urgent").count()
                context['resolved_count'] = Ticket.objects.filter(
                    ticket_status="Resolved").count()
                context['unresolved_count'] = Ticket.objects.filter(
                    ticket_status="Unsolved").count()
                context['pending_count'] = Ticket.objects.filter(
                    ticket_status="Pending").count()
                context['normal_user_list'] = Ticket.objects.filter(
                    user=self.request.user)
                context['staff_user_list'] = Ticket.objects.filter(
                    assigned_to=self.request.user)
                context['software_tickets'] = Ticket.objects.filter(
                    ticket_section='Software').count()
                context['hardware_tickets'] = Ticket.objects.filter(
                    ticket_section='Hardware').count()
                context['applications_tickets'] = Ticket.objects.filter(
                    ticket_section='Applications').count()
                context['infracture_tickets'] = Ticket.objects.filter(
                    ticket_section='Infrastructure and Networking').count()
                context['dbadmin_tickets'] = Ticket.objects.filter(
                    ticket_section='Database').count()
                context['technical_tickets'] = Ticket.objects.filter(
                    ticket_section='Technical').count()
                context['hr_tickets'] = Ticket.objects.filter(
                    ticket_section='HR').count()
                context['general_tickets'] = Ticket.objects.filter(
                    ticket_section='General').count()

            elif self.request.user.is_staff:
                context['all_issues'] = Ticket.objects.filter(
                    assigned_to=self.request.user).count()
                context['urgent_count'] = Ticket.objects.filter(
                    assigned_to=self.request.user, ticket_priority="Urgent").count()
                context['resolved_count'] = Ticket.objects.filter(
                    assigned_to=self.request.user, ticket_status="Resolved").count()
                context['unresolved_count'] = Ticket.objects.filter(
                    assigned_to=self.request.user, ticket_status="Unsolved").count()
                context['pending_count'] = Ticket.objects.filter(
                    ticket_status="Pending").count()
                context['normal_user_list'] = Ticket.objects.filter(
                    user=self.request.user)
                context['staff_user_list'] = Ticket.objects.filter(
                    assigned_to=self.request.user)

                context['software_tickets'] = Ticket.objects.filter(
                    ticket_section='Software', assigned_to=self.request.user).count()
                context['hardware_tickets'] = Ticket.objects.filter(
                    ticket_section='Hardware', assigned_to=self.request.user).count()
                context['applications_tickets'] = Ticket.objects.filter(
                    ticket_section='Applications', assigned_to=self.request.user).count()
                context['infracture_tickets'] = Ticket.objects.filter(
                    ticket_section='Infrastructure and Networking', assigned_to=self.request.user).count()
                context['dbadmin_tickets'] = Ticket.objects.filter(
                    ticket_section='Database', assigned_to=self.request.user).count()
                context['technical_tickets'] = Ticket.objects.filter(
                    ticket_section='Technical').count()
                context['hr_tickets'] = Ticket.objects.filter(
                    ticket_section='HR').count()
                context['general_tickets'] = Ticket.objects.filter(
                    ticket_section='General').count()

            return context
        except Exception as e:
            print(e)


class TicketDetailView(LoginRequiredMixin, generic.DetailView):
    model = Ticket

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(
            ticket=self.get_object()).order_by('-created_date')
        form = EmaiailAttachmentForm
        context['email_form'] = form
        return context


class TicketCreateView(LoginRequiredMixin, generic.CreateView):
    model = Ticket
    form_class = TicketForm

    def form_valid(self, form):
        try:
            form.instance.user = self.request.user
            super().form_valid(form)  # create ticket object
            ticket = self.object
            # add attachments if any
            files = self.request.FILES.getlist('attach')
            if files:
                for file in files:
                    ticket.mediafiles_set.get_or_create(file=file)
            # send mail if true
            config = OutgoinEmailSettings.objects.all()[0]
            if config.send_auto_email_on_ticket_creation:
                attachments = []
                subject = "Issue received"
                receipient_list = [self.request.POST['customer_email'], ]
                print(receipient_list)
                message = config.code_for_automated_reply.replace(
                    '[id]', ticket.ticket_id).replace('[request_description]', ticket.issue_description).replace('[tags]', 'None').replace('[date]', str(timezone.now()))
                # send mail to client
                send_email(self.request,
                           subject, message, receipient_list, attachments)
            if config.send_auto_email_on_agent_assignment:
                # send mail to assignee
                domain = self.request.META['HTTP_HOST']
                protocol = 'https' if self.request.is_secure() else 'http'
                ticket_url = protocol+"://"+domain + \
                    '/ticket-detail/{}/'.format(ticket.id)
                message = config.code_for_automated_assign.replace(
                    '[id]', ticket.ticket_id).replace('[request_description]', ticket.issue_description).replace('[tags]', 'None').replace('[date]', str(timezone.now())).replace('[ticket_link]', ticket_url).replace('[assignee]', ticket.assigned_to.username)
                receipient_list = [ticket.assigned_to.email, ]
                print("receipient_list:".format(receipient_list))
                send_email(self.request, "Ticket assignmet:(#{})".format(
                    ticket.ticket_id), message, receipient_list, files)
        except Exception as e:
            print("ticket create error:{}".format(e))
        return redirect('ticketapp:ticket-list')


class TicketUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Ticket
    form_class = TicketUpdateForm
    template_name = 'ticketapp/ticket_update.html'


class TicketDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Ticket
    success_url = reverse_lazy('ticketapp:ticket-list')


@login_required
def ticket_list(request):
    if request.user.is_superuser:
        tickets = Ticket.objects.all()
    else:
        tickets = Ticket.objects.filter(
            assigned_to=request.user)
    return render(request, 'ticketapp/allissues.html', {'tickets': tickets})


@login_required
def urgent_ticket_list(request):
    if request.user.is_superuser:
        tickets = Ticket.objects.filter(
            ticket_priority='Urgent')
    else:
        tickets = Ticket.objects.filter(
            assigned_to=request.user, ticket_priority='Urgent')
    return render(request, 'ticketapp/urgent.html', {'tickets': tickets})


@login_required
def resolved_tickets(request):
    if request.user.is_superuser:
        tickets = Ticket.objects.filter(
            ticket_status="Resolved")
    else:
        tickets = Ticket.objects.filter(
            assigned_to=request.user,  ticket_status="Resolved")
    return render(request, 'ticketapp/closed.html', {'tickets': tickets})


@login_required
def unresolved_tickets(request):
    if request.user.is_superuser:
        tickets = Ticket.objects.filter(
            ticket_status="Unsolved")
    else:
        tickets = Ticket.objects.filter(
            assigned_to=request.user, ticket_status="Unsolved")
    return render(request, 'ticketapp/open.html', {'tickets': tickets})


@login_required
def mark_ticket_as_resolved(request, id):
    try:
        if request.method == 'POST':
            comment = request.POST['subject']
            ticket = Ticket.objects.get(id=id)
            user = request.user
            date_time = datetime.datetime.now()
            ticket.resolved_by = user
            ticket.resolved_date = date_time
            ticket.ticket_status
            config = OutgoinEmailSettings.objects.all()[0]
            Comment.objects.create(ticket=ticket, user=user, text=comment)
            message = config.code_for_agent_reply.replace(
                '[id]', ticket.ticket_id).replace('[tags]', 'None').replace('[date]', str(timezone.now()))
            subject = 'Ticket[#{}]: Updated'.format(ticket.ticket_id)
            print("Close ticket:{}".format(request.POST.get('closeticket')))
            if request.POST.get('closeticket') == 'on':
                Ticket.objects.filter(id=id).update(
                    ticket_status="Resolved", resolved_by=user, resolved_date=date_time)
                message = 'Your ticket (#({}) has been close by {}.\nIf you are not fully satisfied with the issue,submit another ticket to Helpdesk'.format(
                    ticket.ticket_id, user)
                subject = 'Ticket:(#{}) Closed'.format(ticket.ticket_id)
            recipient_list = [ticket.customer_email, ]
            print("recipient_list:{}".format(recipient_list))
            print("subject:{}".format(subject))
            print("message:{}".format(message))
            print("Files:{}".format(
                request.FILES.getlist('attach')))
            if len(request.FILES.getlist('attach')) > 0:
                attachments = request.FILES.getlist('attach')
            else:
                attachments = []
            send_email(request,
                       subject, message, recipient_list, attachments)
    except Exception as e:
        print(e)
    return HttpResponseRedirect(reverse("ticketapp:ticket-detail", kwargs={'pk': id}))


@login_required
def mark_ticket_as_unresolved(request, id):
    Ticket.objects.filter(id=id).update(ticket_status="Unsolved")
    return HttpResponseRedirect(reverse("ticketapp:ticket-detail", kwargs={'pk': id}))


@login_required
def add_comment(request, ticket_id):
    if request.method == 'POST':
        comment = request.POST['comment']
        ticket = Ticket.objects.get(id=ticket_id)
        user = request.user
        date_time = datetime.datetime.now()
        ticket.resolved_by = user
        ticket.resolved_date = date_time
        ticket.ticket_status

        Comment.objects.create(ticket=ticket, user=user, text=comment)
        return HttpResponseRedirect(reverse("ticketapp:ticket-detail", kwargs={'pk': ticket_id}))


class SearchResultView(LoginRequiredMixin, generic.ListView):
    model = Ticket
    template_name = 'ticketapp/search_results.html'

    def get_queryset(self):
        query = self.request.GET.get("q")
        object_list = Ticket.objects.filter(
            Q(title__icontains=query) | Q(customer_full_name__icontains=query) | Q(
                issue_description__icontains=query)
        ).filter(user=self.request.user)

        return object_list


class StaffSearchResultView(LoginRequiredMixin, generic.ListView):
    model = Ticket
    template_name = 'ticketapp/staff_search_results.html'

    def get_queryset(self):
        query = self.request.GET.get("q")
        object_list = Ticket.objects.filter(
            Q(title__icontains=query) | Q(customer_full_name__icontains=query) | Q(
                issue_description__icontains=query)
        ).filter(assigned_to=self.request.user)

        return object_list


class AllSearchResultView(LoginRequiredMixin, generic.ListView):
    model = Ticket
    template_name = 'ticketapp/staff_search_results.html'

    def get_queryset(self):
        query = self.request.GET.get("q")
        object_list = Ticket.objects.filter(
            Q(title__icontains=query) | Q(customer_full_name__icontains=query) | Q(
                issue_description__icontains=query)
        )

        return object_list


class UserPerformanceListView(LoginRequiredMixin, generic.ListView):
    model = Ticket
    template_name = 'ticketapp/charts.html'

    def get_queryset(self):
        queryset = Ticket.objects.values('resolved_by__username').annotate(
            resolved_count=Count('resolved_by'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vals = Ticket.objects.values('resolved_by__username').annotate(
            resolved_count=Count('resolved_by'))
        my_users = [str(x['resolved_by__username']) for x in vals]
        my_users.pop(0)
        print(my_users)
        context['my_users'] = my_users
        user_num_tickets = [i['resolved_count']
                            for i in vals]
        user_num_tickets.pop(0)

        context['user_num_tickets'] = user_num_tickets
        return context


@login_required
def user_performance_details(request, username):
    user = get_object_or_404(User, username=username)
    tickets = Ticket.objects.filter(assigned_to=user)

    resolved_tickets = Ticket.objects.filter(
        assigned_to=user, ticket_status="Solved")
    unresolved_tickets = Ticket.objects.filter(
        assigned_to=user, ticket_status="Unsolved")
    resolved_count = Ticket.objects.filter(
        assigned_to=user, ticket_status="Solved").count()
    unresolved_count = Ticket.objects.filter(
        assigned_to=user, ticket_status="Unsolved").count()

    context = {
        'tickets': tickets,
        'myuser': user,
        'resolved_tickets': resolved_tickets,
        'unresolved_tickets': unresolved_tickets,
        'resolved_count': resolved_count,
        'unresolved_count': unresolved_count
    }

    return render(request, 'ticketapp/user_performance_detail.html', context)


class UserPerformanceDetailView(LoginRequiredMixin, generic.DetailView):
    model = Ticket
    template_name = 'ticketapp/user_performance_detail.html'


def add_email(request):
    if request.method == 'POST':
        email = request.POST.get('myemail')
        password = request.POST.get('mypassword')

        EmailDetails.objects.create(email=email, password=password)

        return HttpResponseRedirect('/')

    return render(request, 'ticketapp/add_email.html')


def get_emails(request):
    try:
        imap_settings = ImapSettings.objects.all()[0]
        print(imap_settings.email_id, imap_settings.email_password)
        EmailDownload(request, imap_settings.email_id,
                      imap_settings.email_password).login_to_imap_server()
        messages.success(request, "Emails retrieved successfully")
    except Exception as e:
        print(e)
        messages.error(request, "Failed to retrieve emails")
    return HttpResponseRedirect('/')


# Import mimetypes module
# import os module
# Import HttpResponse module
# Import render module

# Define function to download pdf file using template

def download_file(request, filename=''):
    if filename != '':
        # Define Django project base directory
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Define the full file path
        filepath = BASE_DIR + '/filedownload/Files/' + filename
        # Open the file for reading content
        path = open(filepath, 'rb')
        # Set the mime type
        mime_type, _ = mimetypes.guess_type(filepath)
        # Set the return value of the HttpResponse
        response = HttpResponse(path, content_type=mime_type)
        # Set the HTTP header for sending to browser
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        # Return the response value
        return response
    else:
        # Load the template
        return redirect('ticketapp:ticket-list')
