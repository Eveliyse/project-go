# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_address_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='postcode',
            field=models.CharField(max_length=10, validators=[django.core.validators.RegexValidator(regex=b'^[a-zA-Z][a-zA-Z][0-9][0-9a-zA-Z]?[ |-]?[0-9][a-zA-Z]{2}$', message=b'Your postcode was not in the correct format', code=b'invalid_postcode')]),
        ),
    ]
