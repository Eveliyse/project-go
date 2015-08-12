# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0006_rewardpledge'),
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
        migrations.AddField(
            model_name='pledge',
            name='rewards',
            field=models.ManyToManyField(to='projects.Reward'),
        ),
        migrations.AddField(
            model_name='reward',
            name='project',
            field=models.ForeignKey(default=0, to='projects.Project'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='RewardPledge',
        ),
    ]
