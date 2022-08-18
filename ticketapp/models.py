from django.db import models
from django.contrib.auth.models import User
from django.db.models.base import ModelState
from django.forms import PasswordInput
from django.urls import reverse
from django.utils.crypto import get_random_string
from tinymce import models as tinymce_models
# Create your models here.


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
    TICKET_URGENCY = (
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Urgent', 'Urgent'),
    )
    TICKET_STATUSES = (
        ('Pending', 'Pending'),
        ('Resolved', 'Resolved'),
        ('Unsolved', 'Unsolved'),
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
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
        max_length=100, null=True, blank=True, default="Low")
    completed_status = models.BooleanField(default=False)
    assigned_to = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='assigned_to', null=True, blank=True)
    resolved_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='resolved_by', null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    resolved_date = models.DateTimeField(null=True, blank=True)

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
    text = models.CharField(max_length=500)
    created_date = models.DateTimeField(null=True, auto_now_add=True)


class EmailDetails(models.Model):
    email = models.EmailField(max_length=254)
    password = models.CharField(max_length=254)

    def __str__(self):
        return self.email
