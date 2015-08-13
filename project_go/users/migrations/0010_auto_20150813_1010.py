# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20150813_0956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='resident',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
