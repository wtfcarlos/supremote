# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remotes', '0002_auto_20150104_1822'),
        ('invitations', '0002_auto_20150104_1927'),
    ]

    operations = [
        migrations.AddField(
            model_name='invitation',
            name='remote',
            field=models.ForeignKey(default=1, to='remotes.Remote'),
            preserve_default=False,
        ),
    ]
