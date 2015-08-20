# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0014_project_created_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pledge',
            name='project',
            field=models.ForeignKey(related_name='project_pledges', to='projects.Project'),
        ),
        migrations.AlterField(
            model_name='userpledge',
            name='pledge',
            field=models.ForeignKey(related_name='pledged_users', to='projects.Pledge'),
        ),
        migrations.AlterField(
            model_name='userpledge',
            name='user',
            field=models.ForeignKey(related_name='user_pledges', to=settings.AUTH_USER_MODEL),
        ),
    ]
