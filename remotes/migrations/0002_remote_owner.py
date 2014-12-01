# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('remotes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='remote',
            name='owner',
            field=models.ForeignKey(default=1, to='users.Developer'),
            preserve_default=False,
        ),
    ]
