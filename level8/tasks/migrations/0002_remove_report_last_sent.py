# Generated by Django 4.0.1 on 2022-02-24 13:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='report',
            name='last_sent',
        ),
    ]
