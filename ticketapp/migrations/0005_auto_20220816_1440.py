# Generated by Django 3.2.13 on 2022-08-16 11:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ticketapp', '0004_auto_20220816_1420'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='ticket_section',
            field=models.CharField(blank=True, choices=[('Software', 'Software'), ('Hardware', 'Hardware'), ('Applications', 'Applications'), ('Infrastructure and Networking', 'Infrastructure and Networking'), ('Database', 'Database'), ('Technical', 'Technical'), ('HR', 'HR'), ('Administration', 'Administration'), ('Transport', 'Transport'), ('General', 'General')], default='General', max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
