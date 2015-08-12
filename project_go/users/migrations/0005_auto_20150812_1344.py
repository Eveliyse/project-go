# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20150811_1139'),
    ]

    operations = [
        migrations.CreateModel(
            name='Gender',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gender', models.CharField(unique=True, max_length=15)),
            ],
        ),
        migrations.AddField(
            model_name='member',
            name='gender',
            field=models.ForeignKey(default=0, to='users.Gender'),
            preserve_default=False,
        ),
    ]
