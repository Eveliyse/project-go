# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20150812_1348'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='active',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]
