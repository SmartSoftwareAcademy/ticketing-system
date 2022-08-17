# Generated by Django 3.2.13 on 2022-08-16 19:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ticketapp', '0010_auto_20220816_2139'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='attachments',
        ),
        migrations.AddField(
            model_name='mediafiles',
            name='ticket',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ticketapp.ticket'),
        ),
    ]
