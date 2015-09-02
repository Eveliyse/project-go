# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0015_auto_20150820_0915'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='created_date',
            new_name='open_date',
        ),
    ]
