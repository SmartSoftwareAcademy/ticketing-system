from email.headerregistry import Group
from urllib import request
from pytz import timezone
from email import message
from django.shortcuts import render
from django.http.response import HttpResponse
import os
import random
import mimetypes
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
from django.utils import timezone
import re
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail import EmailMessage
from django.utils.html import strip_tags
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.contrib.sites.models import Site


def send_email(request, subject, body, to, attachments):
    try:
        config = OutgoinEmailSettings.objects.all()[0]
        # print(imap_settings.email_id, imap_settings.email_password)
        backend = EmailBackend(host=config.email_host, port=config.email_port, username=config.support_reply_email,
                               password=config.email_password, use_tls=config.use_tls, fail_silently=config.fail_silently)
        # replace &nbsp; with space
        message = re.sub(r'(?<!&nbsp;)&nbsp;', ' ', strip_tags(body))
        if attachments:
            email = EmailMessage(
                subject=subject, body=message, from_email=config.support_reply_email, to=to, connection=backend)
            for attch in attachments:
                # filename = str(protocol+'\\'+str(domain)+'\\'+str(attch.file))
                # print(filename)
                email.attach(attch.name, attch.read(),
                             attch.content_type)
            email.send()
            # messages.success(request, 'Email sent successfully!')
        else:
            email = EmailMessage(
                subject=subject, body=message, from_email=config.support_reply_email, to=to, connection=backend)
            email.send()
            # messages.success(request, 'Email sent successfully!')
    except Exception as e:
        print(e)
        # messages.info(request, "Email send error:{}".format(e))


class TicketListView(LoginRequiredMixin, generic.ListView):
    model = Ticket
    template_name = 'ticketapp/index.html'

    def get_context_data(self, **kwargs):
        try:
            global context
            context = super().get_context_data(**kwargs)
            global all_permissions_in_groups
            all_permissions_in_groups = self.request.user.get_group_permissions()
            print(all_permissions_in_groups)
            perm = 'ticketapp.view_ticket'
            if perm in all_permissions_in_groups or self.request.user.is_superuser:
                context['all_issues'] = Ticket.objects.all().count()
                if len(self.request.user.groups.filter(name='Admins')) > 0 or self.request.user.is_superuser:
                    context['is_admin'] = True
                else:
                    context['is_admin'] = False
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

                # priority
                context['urgent_tag_count'] = Ticket.objects.filter(
                    ticket_priority='Urgent').count()
                context['high_tag_count'] = Ticket.objects.filter(
                    ticket_priority='High').count()
                context['normal_tag_count'] = Ticket.objects.filter(
                    ticket_priority='Normal').count()
                context['medium_tag_count'] = Ticket.objects.filter(
                    ticket_priority='Medium').count()
                context['low_tag_count'] = Ticket.objects.filter(
                    ticket_priority='Low').count()

                # avg time taken to ressolve

                # first reply time
                context['agents'] = [
                    user.username for user in User.objects.filter(groups__name='Agents')]
                # no of tickets per day
            else:
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
        global all_permissions_in_groups
        all_permissions_in_groups = self.request.user.get_group_permissions()
        perm = 'ticketapp.view_ticket'
        delperm = 'ticketapp.delete_ticket'
        context = {}
        if perm not in all_permissions_in_groups:
            return context
        else:
            context = super().get_context_data(**kwargs)
            if delperm in all_permissions_in_groups:
                context['delete_perm'] = True
            else:
                context['delete_perm'] = False
            context['comments'] = Comment.objects.filter(
                ticket=self.get_object()).order_by('-created_date')
            ticket = self.get_object()
            form = EmaiailAttachmentForm
            context['email_form'] = form
            context['users'] = User.objects.all().exclude(username='chatbot')
            context['ticket_ids'] = Ticket.objects.all().exclude(
                id=self.get_object().id)
            context['days'] = timezone.now().day - ticket.created_date.day
            context['hours'] = timezone.now().hour - ticket.created_date.hour
            context['mins'] = timezone.now().minute - \
                ticket.created_date.minute
            context['agent_voice'] = Comment.objects.filter(
                ticket=self.get_object()).count()
            ticket_settings = TicketSettings.objects.all().first()
            context['escallate_hours'] = ticket_settings.duration_before_escallation
            if ticket_settings.enable_ticket_escalltion:
                if len(ticket.assigned_to.groups.filter(name="Admins")) <= 0 and (ticket.ticket_status == "Unsolved" or ticket.ticket_status == "Pending"):
                    escallate_time = ticket.created_date
                    escallate_time += timedelta(
                        hours=int(ticket_settings.duration_before_escallation))
                    now = timezone.now()
                    context['escallate_time'] = escallate_time-now
            return context


class TicketCreateView(LoginRequiredMixin, generic.CreateView):
    model = Ticket
    form_class = TicketForm

    def get_context_data(self, **kwargs):
        global all_permissions_in_groups
        all_permissions_in_groups = self.request.user.get_group_permissions()
        perm = 'ticketapp.add_ticket'
        if perm not in all_permissions_in_groups:
            context = {}
        else:
            context = super().get_context_data(**kwargs)
            context['tags'] = Tags.objects.all()
        return context

    def form_valid(self, form):
        try:
            load_time_zone()
            form.instance.ticket_status="Pending"
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

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        self.referer = request.META.get("HTTP_REFERER", "")
        request.session["login_referer"] = self.referer
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        global all_permissions_in_groups
        all_permissions_in_groups = self.request.user.get_group_permissions()
        perm = 'ticketapp.change_ticket'
        if perm not in all_permissions_in_groups:
            context = {}
        else:
            context = super().get_context_data(**kwargs)
            context['tags'] = Tags.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        self.referer = request.session.get("login_referer", "")
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        redirect_url = super().form_valid(form)
        config = OutgoinEmailSettings.objects.all()[0]
        ticket = self.object
        prev_assignee = str(ticket.assigned_to.username)
        tags = self.request.POST.getlist("tag_names")
        print(ticket)
        print(tags)
        for tag_name in tags:
            ticket.tags.add(int(tag_name))
        ticket.save()
        domain = Site.objects.get_current().domain
        to_list = [ticket.assigned_to.email, ]
        tag_list = ''
        tags = ticket.tags.all()
        for tag in tags:
            tag_list += str(tag.tag_name)
        attachments = []
        ticket_url = '{}/ticket-detail/{}/'.format(domain, ticket.id)
        if str(ticket.assigned_to.username) != prev_assignee:
            message = config.code_for_automated_assign.replace(
                '[id]', ticket.ticket_id).replace('[request_description]', ticket.issue_description).replace('[tags]', tag_list).replace('[date]', str(timezone.now())).replace('[ticket_link]', ticket_url).replace('[assignee]', ticket.assigned_to.username)
            subject = "Ticket[#{}] assigned to you".format(ticket.ticket_id)
        else:
            message = "Ticket:[#{}] has been updated by {} as follows\n\nTags:{}\nTicket Priority:{}\n\n\nRegars,\nHelpdesk.".format(
                ticket.ticket_id, str(self.request.user.username), tag_list, ticket.ticket_priority)
            subject = "Ticket:[#{}] updated".format(ticket.ticket_id)
        print("recipient list:".format(to_list))
        send_email(self.request, subject, message,
                   to_list, attachments)
        messages.info(self.request, "Ticket updates saved!")
        return redirect_url


class TicketDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Ticket
    success_url = reverse_lazy('ticketapp:ticket-list')


@login_required
def ticket_list(request):
    global all_permissions_in_groups
    all_permissions_in_groups = request.user.get_group_permissions()
    perm = 'ticketapp.view_ticket'
    if request.user.is_superuser or perm in all_permissions_in_groups:
        tickets = Ticket.objects.all().order_by('-created_date')
    else:
        tickets = Ticket.objects.filter(
            assigned_to=request.user).order_by('-created_date')
    return render(request, 'ticketapp/allissues.html', {'tickets': tickets})


@login_required
def urgent_ticket_list(request):
    global all_permissions_in_groups
    all_permissions_in_groups = request.user.get_group_permissions()
    perm = 'ticketapp.view_ticket'
    if request.user.is_superuser or perm in all_permissions_in_groups:
        tickets = Ticket.objects.filter(
            ticket_priority='Urgent')
    else:
        tickets = Ticket.objects.filter(
            assigned_to=request.user, ticket_priority='Urgent')
    return render(request, 'ticketapp/urgent.html', {'tickets': tickets})


@login_required
def pending_ticket_list(request):
    global all_permissions_in_groups
    all_permissions_in_groups = request.user.get_group_permissions()
    perm = 'ticketapp.view_ticket'
    if request.user.is_superuser or perm in all_permissions_in_groups:
        tickets = Ticket.objects.filter(
            ticket_status='Pending').order_by('-created_date')
    else:
        tickets = Ticket.objects.filter(
            assigned_to=request.user, ticket_status='Pending')
    return render(request, 'ticketapp/pending.html', {'tickets': tickets})


@login_required
def resolved_tickets(request):
    global all_permissions_in_groups
    all_permissions_in_groups = request.user.get_group_permissions()
    perm = 'ticketapp.view_ticket'
    if request.user.is_superuser or perm in all_permissions_in_groups:
        tickets = Ticket.objects.filter(
            ticket_status="Resolved").order_by('-created_date')
    else:
        tickets = Ticket.objects.filter(
            assigned_to=request.user,  ticket_status="Resolved").order_by('-created_date')
    return render(request, 'ticketapp/closed.html', {'tickets': tickets})


@login_required
def unresolved_tickets(request):
    perm = 'ticketapp.view_ticket'
    if request.user.is_superuser or perm in all_permissions_in_groups:
        tickets = Ticket.objects.filter(
            ticket_status="Unsolved").order_by('-created_date')
    else:
        tickets = Ticket.objects.filter(
            assigned_to=request.user, ticket_status="Unsolved").order_by('-created_date')
    return render(request, 'ticketapp/open.html', {'tickets': tickets})


@login_required
def ticket_bulk_edit(request):
    try:
        global all_permissions_in_groups
        all_permissions_in_groups = request.user.get_group_permissions()
        perm = 'ticketapp.change_ticket'
        if perm not in all_permissions_in_groups:
            if not request.user.is_superuser:
                messages.warning(request, 'Permission denied!')
            return redirect('ticketapp:ticket-list')
        mark_as = request.POST.get('hiddenfield')
        ticket_ids = request.POST.getlist('check[]')
        message = ""
        print(mark_as)
        for id in ticket_ids:
            if mark_as == 'pending':
                ticket = Ticket.objects.get(id=int(id))
                ticket.ticket_status = "Pending"
                ticket.updated_by = request.user
                ticket.last_updated = timezone.now()
                ticket.save()
                content = 'Your ticket (#({}) has been marked PENDING by {}.'.format(
                    ticket.ticket_id, request.user)
                subject = 'Ticket:(#{}) Updated'.format(ticket.ticket_id)
                recipient_list = []
                recipient_list.append(ticket.customer_email)
                send_email(request, subject, content, recipient_list, [])
                message = "Ticket(s) marked as pending successfully!"
            elif mark_as == 'solved':
                ticket = Ticket.objects.get(id=int(id))
                ticket.ticket_status = "Resolved"
                ticket.updated_by = request.user
                ticket.last_updated = timezone.now()
                ticket.resolved_by = request.user
                ticket.resolved_date = timezone.now()
                ticket.save()
                content = 'Your ticket (#({}) has been closed by {}.\nIf you are not fully satisfied with the issue,submit another ticket to Helpdesk'.format(
                    ticket.ticket_id, request.user)
                subject = 'Ticket:(#{}) Closed'.format(ticket.ticket_id)
                recipient_list = []
                recipient_list.append(ticket.customer_email)
                send_email(request, subject, content, recipient_list, [])
                message = "Ticket(s) marked as Solved successfully!"
            elif mark_as == 'unsolved':
                Ticket.objects.filter(id=int(id)).update(
                    ticket_status="Unsolved", updated_by=request.user, last_updated=timezone.now())
                message = "Ticket(s) marked as Unsolved successfully!"
            elif mark_as == 'delete':
                Ticket.objects.filter(id=int(id)).delete()
                message = "Ticket(s) deleted successfully!"
        messages.success(request, message)
        if mark_as == 'edit':
            id = int(ticket_ids[0])
            return HttpResponseRedirect(reverse("ticketapp:update-ticket", kwargs={'pk': id}))
    except Exception as e:
        print("Bulk edit error:{}".format(e))
    return redirect("ticketapp:ticket-list")


@login_required
def mark_ticket_as_resolved(request, id):
    try:
        perm = 'ticketapp.change_ticket'
        if not request.user.is_superuser or perm not in all_permissions_in_groups:
            messages.warning(request, 'Permission denied!')
            return redirect('ticketapp:ticket-list')
        load_time_zone()
        if request.method == 'POST':
            comment = request.POST['subject']
            ticket = Ticket.objects.get(id=id)
            user = request.user
            date_time = datetime.now()
            ticket.resolved_by = user
            ticket.resolved_date = date_time
            ticket.ticket_status
            config = OutgoinEmailSettings.objects.all()[0]
            Comment.objects.create(ticket=ticket, user=user, text=comment)
            conversions = Comment.objects.all()
            conversion = ''
            for comment in conversions:
                conversion += "\n"+str(comment.text)
            message = config.code_for_agent_reply.replace(
                '[id]', ticket.ticket_id).replace('[tags]', 'None').replace('[date]', str(datetime.now())).replace('[conversation_history]', conversion)
            subject = 'Ticket[#{}]: Updated'.format(ticket.ticket_id)
            print("Close ticket:{}".format(
                request.POST.get('closeticket')))
            if request.POST.get('closeticket') == 'on':
                Ticket.objects.filter(id=id).update(
                    ticket_status="Resolved", resolved_by=user, resolved_date=date_time)
                message = 'Your ticket (#({}) has been closed by {}.\nIf you are not fully satisfied with the issue,submit another ticket to Helpdesk'.format(
                    ticket.ticket_id, user)
                subject = 'Ticket:(#{}) Closed'.format(ticket.ticket_id)
            recipient_list = request.POST.getlist('cc')
            recipient_list.append(ticket.customer_email)
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
    perm = 'ticketapp.change_ticket'
    if not request.user.is_superuser or perm not in all_permissions_in_groups:
        messages.warning(request, 'Permission denied!')
        return redirect('ticketapp:ticket-list')
    ticket = Ticket.objects.get(id=id)
    ticket.ticket_status = "Unresolved"
    ticket.save()
    message = 'Your ticket (#({}) has been re-opened by {}.\nFor any queries,submit another ticket to Helpdesk'.format(
        ticket.ticket_id, request.user.username)
    subject = 'Ticket:(#{}) Re-opened'.format(ticket.ticket_id)
    recipient_list = [ticket.customer_email, ]
    attachments = []
    send_email(request,
               subject, message, recipient_list, attachments)
    return HttpResponseRedirect(reverse("ticketapp:ticket-detail", kwargs={'pk': id}))


@login_required
def mark_ticket_as_pending(request, id):
    perm = 'ticketapp.change_ticket'
    if not request.user.is_superuser or perm not in all_permissions_in_groups:
        messages.warning(request, 'Permission denied!')
        return redirect('ticketapp:ticket-list')
    ticket = Ticket.objects.get(id=id)
    ticket.ticket_status = "Pending"
    ticket.save()
    message = 'Ticket (#({}) status changed to Pending by {}.\nFor any queries,submit another ticket to Helpdesk'.format(
        ticket.ticket_id, request.user.username)
    subject = 'Ticket:(#{}) status changed'.format(ticket.ticket_id)
    recipient_list = [ticket.customer_email, ]
    attachments = []
    send_email(request,
               subject, message, recipient_list, attachments)
    return HttpResponseRedirect(reverse("ticketapp:ticket-detail", kwargs={'pk': id}))


@login_required
def add_comment(request, ticket_id):
    perm = 'ticketapp.change_ticket'
    if not request.user.is_superuser or perm not in all_permissions_in_groups:
        messages.warning(request, 'Permission denied!')
        return redirect('ticketapp:ticket-list')
    if request.method == 'POST':
        comment = request.POST['comment']
        ticket = Ticket.objects.get(id=ticket_id)
        user = request.user
        date_time = datetime.now()
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
        load_time_zone()
        imap_settings = ImapSettings.objects.all()[0]
        print(imap_settings.email_id, imap_settings.email_password)
        EmailDownload(request, imap_settings.email_id,
                      imap_settings.email_password).login_to_imap_server()
        messages.success(request, "Emails retrieved successfully")
    except Exception as e:
        print(e)
        messages.error(request, "Failed to retrieve emails")
    return redirect('ticketapp:all-tickets')

# Ticket escalation


class Escallate:

    def __init__(self, request):
        """Yeah, initializing everything"""
        self.request = request

    def ticket_escallation(self):
        from pytz import timezone
        try:
            tickets = Ticket.objects.all()
            top_assignees = User.objects.filter(groups__name='Admins')
            # escallate after time specified
            ticket_settings = TicketSettings.objects.all().first()
            time_zone = str(ticket_settings.time_zone)
            tz = timezone(time_zone)
            for t in tickets:
                if str(t.ticket_status).lower() == 'unsolved' or str(t.ticket_status).lower() == 'pending':
                    if len(t.assigned_to.groups.filter(name='Admins')) <= 0:
                        time_to_escallate = t.created_date.astimezone(tz)
                        time_to_escallate += timedelta(
                            hours=int(ticket_settings.duration_before_escallation))
                        today = datetime.now()
                        # print(today)
                        # print(time_to_escallate)
                        second_diff = today.second - time_to_escallate.second
                        if (today.day == time_to_escallate.day) and (today.hour == time_to_escallate.hour) and (today.minute == time_to_escallate.minute) and (second_diff >= 0 or second_diff <= 20):
                            print("Escallation in progress...")
                            prev_assignee = t.assigned_to
                            assignee = random.choice(top_assignees)
                            t.assigned_to = assignee
                            t.save()
                            attachments = []
                            subject = "Ticket:[#{}] escallation".format(
                                t.ticket_id)
                            domain = Site.objects.get_current().domain
                            # domain = self.request.META['HTTP_HOST']
                            # protocol = 'https' if self.request.is_secure() else 'http'
                            ticket_url = '{}/ticket-detail/{}/'.format(
                                domain, t.ticket_id)
                            receipient_list = [assignee.email, ]
                            message = ticket_settings.code_for_automated_escallation_email.replace('[id]', t.ticket_id).replace('[request_description]', t.issue_description).replace('[tags]', 'None').replace('[date]', str(datetime.now(
                            ))).replace('[prev_assignee]', prev_assignee.username).replace('[asignee]', assignee.username).replace('[hours]', str(ticket_settings.duration_before_escallation)).replace('[ticket_link]', str(ticket_url))
                            # send mail to assignee
                            send_email(self.request,
                                       subject, message, receipient_list, attachments)
                            # send maill to client
                            send_email(self.request, subject, "Your Ticket:[{}] has been escallated to Top Helpdesk Officials due to possible delay in reply within {} hours.".format(
                                t.ticket_id, str(ticket_settings.duration_before_escallation)), [t.customer_email, ], attachments)
        except Exception as e:
            print(e)
        # print("Escallate Ticket:[#{}] to {}".format(t.ticket_id, assignee.username))
# Define function to download pdf file using template


# def check_user_perm(request):
#     from django.contrib.auth.models import Group
#     permissions = []
#     for group in Group.objects.all():
#         permissions = group.permissions.all()
#     print(permissions)


def load_time_zone():
    import django.utils.timezone
    from pytz import timezone

    ticket_settings = TicketSettings.objects.all().first()
    time_zone = str(ticket_settings.time_zone)
    tz = timezone(time_zone)
    if tz:
        django.utils.timezone.activate(tz)
    else:
        django.utils.timezone.deactivate()


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
