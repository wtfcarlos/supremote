# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remotes', '0002_auto_20150104_1822'),
    ]

    operations = [
        migrations.AddField(
            model_name='remote',
            name='endpoint',
            field=models.URLField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
