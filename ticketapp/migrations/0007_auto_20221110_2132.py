# Generated by Django 3.2.5 on 2022-11-10 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketapp', '0006_auto_20221110_2115'),
    ]

    operations = [
        migrations.AddField(
            model_name='system_settings',
            name='city',
            field=models.CharField(blank=True, default='Nairobi', max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='system_settings',
            name='country',
            field=models.CharField(blank=True, default='Kenya', max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='system_settings',
            name='email',
            field=models.EmailField(blank=True, default='user@example.com', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='system_settings',
            name='road',
            field=models.CharField(blank=True, default='Mombasa Road', max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='system_settings',
            name='state',
            field=models.CharField(blank=True, default='Kenya', max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='system_settings',
            name='suite',
            field=models.CharField(blank=True, default='First Floor Birdir Complex,', max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='system_settings',
            name='tel',
            field=models.CharField(blank=True, default='+254743793901', max_length=15, null=True),
        ),
    ]
