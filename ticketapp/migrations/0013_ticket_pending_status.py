# Generated by Django 3.2.13 on 2022-08-24 22:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketapp', '0012_alter_tags_tag_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='pending_status',
            field=models.BooleanField(default=False),
        ),
    ]
