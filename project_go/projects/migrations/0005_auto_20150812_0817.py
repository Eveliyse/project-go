# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_auto_20150812_0810'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rewardpledge',
            name='pledge',
        ),
        migrations.RemoveField(
            model_name='rewardpledge',
            name='reward',
        ),
        migrations.DeleteModel(
            name='RewardPledge',
        ),
    ]
