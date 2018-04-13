# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-04-12 11:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0012_auto_20180406_2211'),
    ]

    operations = [
        migrations.CreateModel(
            name='CDR',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('acctid', models.BigIntegerField()),
                ('calldate', models.DateTimeField()),
                ('clid', models.CharField(max_length=80, null=True)),
                ('src', models.CharField(max_length=80, null=True)),
                ('dst', models.CharField(max_length=80, null=True)),
                ('dcontext', models.CharField(max_length=80, null=True)),
                ('channel', models.CharField(max_length=80, null=True)),
                ('dstchannel', models.CharField(max_length=80, null=True)),
                ('lastapp', models.CharField(max_length=80, null=True)),
                ('lastdata', models.CharField(max_length=80, null=True)),
                ('duration', models.IntegerField()),
                ('billsec', models.IntegerField()),
                ('enterq', models.DateTimeField()),
                ('leaveq', models.DateTimeField()),
                ('endcall', models.DateTimeField()),
                ('disposition', models.CharField(max_length=45, null=True)),
                ('amaflags', models.IntegerField()),
                ('accountcode', models.CharField(max_length=20, null=True)),
                ('userfield', models.CharField(max_length=225, null=True)),
                ('uniqueid', models.CharField(max_length=32, null=True)),
                ('linkedid', models.CharField(max_length=32, null=True)),
                ('sequence', models.CharField(max_length=32, null=True)),
                ('peeraccount', models.CharField(max_length=32, null=True)),
                ('import_cdr', models.IntegerField()),
            ],
        ),
    ]
