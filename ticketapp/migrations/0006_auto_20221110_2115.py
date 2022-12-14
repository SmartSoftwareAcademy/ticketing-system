# Generated by Django 3.2.5 on 2022-11-10 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketapp', '0005_auto_20221110_1611'),
    ]

    operations = [
        migrations.AlterField(
            model_name='system_settings',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='logos/'),
        ),
        migrations.AlterField(
            model_name='system_settings',
            name='logo_bg',
            field=models.CharField(blank=True, choices=[('light', 'light'), ('primary', 'primary'), ('secondary', 'secondary'), ('success', 'success'), ('dark', 'dark'), ('default', 'default')], default='light', max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='system_settings',
            name='site_title',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='system_settings',
            name='title_text_color',
            field=models.CharField(blank=True, choices=[('light', 'light'), ('primary', 'primary'), ('secondary', 'secondary'), ('success', 'success'), ('dark', 'dark'), ('default', 'default')], default='primary', max_length=10, null=True),
        ),
    ]
