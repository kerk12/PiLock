# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-06 22:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20170728_2256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accessattempt',
            name='ip',
            field=models.GenericIPAddressField(default='0.0.0.0', protocol='IPv4'),
        ),
    ]
