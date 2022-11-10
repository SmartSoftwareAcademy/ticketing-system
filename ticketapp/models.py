from django.db import models
from django.contrib.auth.models import User
from django.db.models.base import ModelState
from django.forms import PasswordInput
from django.urls import reverse
from django.utils.crypto import get_random_string
from tinymce import models as tinymce_models
import pytz
from timezone_field import TimeZoneField


class Ticket(models.Model):

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
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    tags = models.ManyToManyField('Tags', null=True, blank=True)
    ticket_id = models.CharField(max_length=8, unique=True, blank=True)
    title = models.CharField(max_length=500)
    issue_description = tinymce_models.HTMLField(
        max_length=25000, null=True, blank=True)
    customer_full_name = models.CharField(
        max_length=200, null=True, blank=True)
    customer_phone_number = models.CharField(
        max_length=20, null=True, blank=True)
    customer_email = models.EmailField(
        max_length=40, default='info@tdbsoft.co.ke')
    ticket_section = models.CharField(
        max_length=30, choices=TICKET_SECTIONS, null=True, blank=True, default='General')
    ticket_priority = models.CharField(
        max_length=100, choices=TICKET_PRIORITIES, null=True, blank=True, default="Low")
    ticket_status = models.CharField(
        max_length=100, choices=TICKET_STATUSES, default='Unsolved')
    assigned_to = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='assigned_to', null=True, blank=True)
    resolved_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='resolved_by', null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='updated_by', null=True, blank=True)
    last_updated = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    def generate_client_id(self):
        return get_random_string(8, allowed_chars='0123456789abcdefghijklmnopuwzxyv')

    def get_absolute_url(self):
        return reverse("ticketapp:ticket-detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        self.ticket_id = self.generate_client_id()
        super(Ticket, self).save(*args, **kwargs)


class MediaFiles(models.Model):
    ticket = models.ForeignKey(
        'Ticket', on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to='attachments')

    def __str__(self):
        return self.file.url or None

    class Meta:
        verbose_name_plural = 'Attachments'


class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=500)
    created_date = models.DateTimeField(null=True, auto_now_add=True)

    def __str__(self):
        return self.ticket.title


class Tags(models.Model):
    TICKET_TAGS = (
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('Normal', 'Normal'),
        ('High', 'High'),
        ('Urgent', 'Urgent'),
    )
    #ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    tag_name = models.CharField(
        max_length=100, choices=TICKET_TAGS, default='Normal')

    def __str__(self):
        return self.tag_name

    class Meta:
        verbose_name_plural = 'Tags'


class EmailDetails(models.Model):
    email = models.EmailField(max_length=254)
    password = models.CharField(max_length=254)

    def __str__(self):
        return self.email


class ImapSettings(models.Model):
    imap_server = models.CharField(max_length=100)
    email_id = models.EmailField(max_length=100)
    email_password = models.CharField(max_length=100)
    imap_port = models.IntegerField()
    auto_import_mails_as_tickets = models.BooleanField(
        default=True, blank=True, null=True)

    def __str__(self):
        return self.email_id

    class Meta:
        verbose_name_plural = 'Imap Email Setup - (Incoming)'


class OutgoinEmailSettings(models.Model):
    support_reply_email_name = models.CharField(
        max_length=255, default='ICT Helpdesk', blank=True, null=True)
    support_reply_email = models.EmailField(
        max_length=255, default='titusowuor30@gmail.com', blank=True, null=True)
    email_password = models.CharField(
        max_length=255, default='xdofqrtncuimlewm', blank=True, null=True)
    email_port = models.IntegerField(default=587, blank=True, null=True)
    email_backed = models.CharField(
        max_length=100, default='smtp', blank=True, null=True)
    email_host = models.CharField(
        max_length=255, default='smtp.gmail.com', blank=True, null=True)
    fail_silently = models.BooleanField(default=True, blank=True, null=True)
    use_tls = models.BooleanField(default=True, blank=True, null=True)
    code_place_holders = models.TextField(
        max_length=25000, blank=True, null=True)
    send_auto_email_on_ticket_creation = models.BooleanField(
        default=True, blank=True, null=True)
    auto_assign_tickets = models.BooleanField(
        default=True, blank=True, null=True)
    code_for_automated_reply = models.TextField(
        max_length=25000, blank=True, null=True)
    send_auto_email_on_agent_reply = models.BooleanField(
        default=True, blank=True, null=True)
    send_auto_email_on_agent_assignment = models.BooleanField(
        default=True, blank=True, null=True)
    code_for_automated_assign = models.TextField(
        max_length=25000, blank=True, null=True)
    code_for_agent_reply = models.TextField(
        max_length=25000, blank=True, null=True)

    def __str__(self):
        return self.support_reply_email_name

    class Meta:
        verbose_name_plural = 'Support Email Setup - (Outgoing)'


class TicketSettings(models.Model):
    enable_ticket_escalltion = models.BooleanField(
        default=True, blank=True, null=True)
    time_zone = TimeZoneField(use_pytz=True, default='Africa/Nairobi')
    duration_before_escallation = models.IntegerField(
        default=48, help_text="Time in hours")
    code_place_holders = models.TextField(
        max_length=25000, blank=True, null=True)
    code_for_automated_escallation_email = models.TextField(
        max_length=25000, blank=True, null=True)

    def __str__(self):
        return "Ticket Settings"

    class Meta:
        verbose_name_plural = 'Ticket Settings'

class System_Settings(models.Model):
    COLORS=(
        ('light', 'light'),
        ('primary', 'primary'),
        ('secondary', 'secondary'),
        ('success', 'success'),
         ('dark', 'dark'),
        ('default', 'default'),
    )
    logo=models.ImageField(upload_to='logos/',null=True,blank=True)
    site_title=models.CharField(max_length=100,null=True,blank=True)
    title_text_color=models.CharField(choices=COLORS,default="primary",max_length=10,null=True,blank=True)
    logo_bg=models.CharField(choices=COLORS,max_length=10,default="light",null=True,blank=True)
    email=models.EmailField(max_length=100,default="info@masterspace.co.ke",null=True,blank=True)
    address=models.CharField(max_length=100,default="36779-00200",null=True,blank=True)
    company=models.CharField(max_length=100,default="Gokhan Masterspace JV Limited",null=True,blank=True)
    tel=models.CharField(max_length=15,default="+254743793901",null=True,blank=True)
    suite=models.CharField(max_length=100,default="First Floor Birdir Complex,",null=True,blank=True)
    road=models.CharField(max_length=100,default="Mombasa Road",null=True,blank=True)
    city=models.CharField(max_length=100,default="Nairobi",null=True,blank=True)
    state=models.CharField(max_length=100,default="Kenya",null=True,blank=True)
    country=models.CharField(max_length=100,default="Kenya",null=True,blank=True)

    def __str__(self):
        return "System Settings"

    class Meta:
        verbose_name_plural = 'System Settings'