# Generated by Django 3.2.13 on 2022-08-24 22:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketapp', '0013_ticket_pending_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='completed_status',
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='pending_status',
        ),
        migrations.AddField(
            model_name='ticket',
            name='ticket_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Resolved', 'Resolved'), ('Unsolved', 'Unsolved')], default='Unsolved', max_length=100),
        ),
    ]
