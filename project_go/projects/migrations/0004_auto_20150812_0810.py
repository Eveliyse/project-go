# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_pledge_amount'),
    ]

    operations = [
        migrations.CreateModel(
            name='RewardPledge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pledge', models.ForeignKey(to='projects.Pledge')),
            ],
        ),
        migrations.RemoveField(
            model_name='reward',
            name='pledge',
        ),
        migrations.AddField(
            model_name='rewardpledge',
            name='reward',
            field=models.ForeignKey(to='projects.Reward'),
        ),
    ]
