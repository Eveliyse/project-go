# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_auto_20150813_1436'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='active',
            field=models.BooleanField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='address',
            name='line_2',
            field=models.CharField(default=1, max_length=50, blank=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='member',
            name='gender',
            field=models.ForeignKey(default='1', blank=True, to='users.Gender'),
            preserve_default=False,
        ),
    ]
