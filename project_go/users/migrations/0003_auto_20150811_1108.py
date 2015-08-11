# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20150810_1437'),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.AlterField(
            model_name='address',
            name='line_1',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='address',
            name='line_2',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='address',
            name='postcode',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='address',
            name='town',
            field=models.CharField(max_length=50),
        ),
        migrations.AddField(
            model_name='address',
            name='country',
            field=models.ForeignKey(default='1', to='users.Country'),
            preserve_default=False,
        ),
    ]
