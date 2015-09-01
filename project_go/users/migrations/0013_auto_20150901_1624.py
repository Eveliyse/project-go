# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20150818_0847'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='member',
            name='gender',
            field=models.ForeignKey(to='users.Gender'),
        ),
    ]
