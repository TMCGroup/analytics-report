# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-29 12:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RapidproKey',
            new_name='Workspace',
        ),
    ]
