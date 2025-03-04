from dataclasses import fields
from django.forms import ModelForm, PasswordInput
from email.policy import default
from django import forms
from django.contrib.auth.models import User
from .models import ImapSettings, Tags, Ticket
from tinymce.widgets import TinyMCE
from .custom_widgets import MultipleFileInput

TICKET_SECTIONS = (
    ('Software', 'Software'),
    ('Hardware', 'Hardware'),
    ('Applications', 'Applications'),
    ('Infrastructure and Networking', 'Infrastructure and Networking'),
    ('Database', 'Database'),
    ('Technical', 'Technical'),
    ('HR', 'HR'),
    ('Administration', 'Administration'),
    ('Transport', 'Transport'),
    ('General', 'General'),
)
TICKET_STATUSES = (
    ('Pending', 'Pending'),
    ('Resolved', 'Resolved'),
    ('Unsolved', 'Unsolved'),
)
TICKET_PRIORITIES = (
    ('Low', 'Low'),
    ('Medium', 'Medium'),
    ('Normal', 'Normal'),
    ('High', 'High'),
    ('Urgent', 'Urgent'),
)


class TicketForm(forms.ModelForm):
    title = forms.CharField(max_length=500, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    customer_full_name = forms.CharField(required=False,
                                         max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    customer_phone_number = forms.CharField(required=False,
                                            max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    customer_email = forms.CharField(
        max_length=40, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    issue_description = forms.CharField(required=False,
                                        max_length=25000, widget=TinyMCE(attrs={'cols': 40, 'rows': 10, 'class': 'tinymce'}))
    ticket_section = forms.ChoiceField(
        choices=TICKET_SECTIONS, widget=forms.Select(attrs={'class': 'form-control'}))
    ticket_priority = forms.ChoiceField(
        choices=TICKET_PRIORITIES, widget=forms.Select(attrs={'class': 'form-control'}))
    assigned_to = forms.ModelChoiceField(required=False,
                                         queryset=User.objects.all(), empty_label='Select User', widget=forms.Select(attrs={'class': 'form-control'}))
    # attach = forms.FileField(required=False,
    #                          widget=forms.ClearableFileInput(attrs={'multiple': True}))
    attach = forms.FileField(widget=MultipleFileInput(), required=False)

    class Meta:
        model = Ticket
        exclude = ('user', 'ticket_id', 'created_date',
                   'completed_status', 'resolved_by', 'resolved_date')


class TicketUpdateForm(forms.ModelForm):
    title = forms.CharField(max_length=500, widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'hidden'}))
    customer_full_name = forms.CharField(required=False,
                                         max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'If applicable', 'type': 'hidden'}))
    customer_phone_number = forms.CharField(required=False,
                                            max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'If applicable', 'type': 'hidden'}))
    customer_email = forms.CharField(required=False,
                                     max_length=40, widget=forms.EmailInput(attrs={'class': 'form-control', 'type': 'hidden'}))
    issue_description = forms.CharField(required=False,
                                        max_length=25000, widget=forms.TextInput(attrs={'cols': 40, 'rows': 30, 'class': 'tinymce', 'type': 'hidden'}))
    ticket_section = forms.ChoiceField(
        choices=TICKET_SECTIONS, widget=forms.Select(attrs={'class': 'form-control'}))
    ticket_priority = forms.ChoiceField(required=False,
                                        choices=TICKET_PRIORITIES, widget=forms.Select(attrs={'class': 'form-control'}))
    ticket_status = forms.ChoiceField(required=False,
                                      choices=TICKET_STATUSES, widget=forms.Select(attrs={'class': 'form-control', 'type': 'hidden'}))
    assigned_to = forms.ModelChoiceField(required=False,
                                         queryset=User.objects.all(), empty_label='Select User', widget=forms.Select(attrs={'class': 'form-control'}))
    # attach = forms.FileField(required=False,
    #                          widget=forms.ClearableFileInput(attrs={'multiple': True}))
    attach = forms.FileField(widget=MultipleFileInput(), required=False)


    class Meta:
        model = Ticket
        exclude = ('user', 'ticket_id', 'created_date',
                   'resolved_by', 'resolved_date')


class EmaiailAttachmentForm(forms.Form):
    subject = forms.CharField(required=False,
                              max_length=25000, widget=TinyMCE(attrs={'cols': 40, 'rows': 30, 'class': 'tinymce', 'placeholder': 'Add note on how issue was solved'}))
    # attach = forms.FileField(required=False,
    #                          widget=forms.ClearableFileInput(attrs={'multiple': True, 'name': 'attach'}))
    attach = forms.FileField(widget=MultipleFileInput(), required=False)


class ImapForm(ModelForm):
   # email_password = forms.CharField(widget=PasswordInput())

    class Meta:
        model = ImapSettings
        fields = '__all__'
