# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_pledge_reward_userpledge'),
    ]

    operations = [
        migrations.AddField(
            model_name='pledge',
            name='amount',
            field=models.DecimalField(default=0, max_digits=12, decimal_places=2),
            preserve_default=False,
        ),
    ]
