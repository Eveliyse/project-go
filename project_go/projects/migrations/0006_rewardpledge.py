# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0005_auto_20150812_0817'),
    ]

    operations = [
        migrations.CreateModel(
            name='RewardPledge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pledge', models.ForeignKey(to='projects.Pledge')),
                ('reward', models.ForeignKey(to='projects.Reward')),
            ],
        ),
    ]
