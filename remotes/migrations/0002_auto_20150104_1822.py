# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remotes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='remote',
            name='developer',
            field=models.ForeignKey(related_name='developer', to='users.User'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='remote',
            name='users',
            field=models.ManyToManyField(to='users.User'),
            preserve_default=True,
        ),
    ]
