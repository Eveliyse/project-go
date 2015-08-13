# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_auto_20150813_0952'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='line_2',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='member',
            name='gender',
            field=models.ForeignKey(blank=True, to='users.Gender', null=True),
        ),
    ]
