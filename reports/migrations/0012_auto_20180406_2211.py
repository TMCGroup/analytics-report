# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-04-06 19:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0011_auto_20180406_2208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artcontact',
            name='area',
            field=models.CharField(max_length=225, null=True),
        ),
        migrations.AlterField(
            model_name='artcontact',
            name='designation',
            field=models.CharField(max_length=225, null=True),
        ),
        migrations.AlterField(
            model_name='artcontact',
            name='district',
            field=models.BigIntegerField(null=True),
        ),
    ]
