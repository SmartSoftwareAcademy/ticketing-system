# Generated by Django 3.2.5 on 2022-11-10 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketapp', '0009_auto_20221110_2202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='system_settings',
            name='address',
            field=models.CharField(blank=True, default='36779-00200', max_length=100, null=True),
        ),
    ]
