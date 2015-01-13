# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remotes', '0004_actionthrottle'),
    ]

    operations = [
        migrations.AddField(
            model_name='actionthrottle',
            name='status_code',
            field=models.PositiveSmallIntegerField(default=200),
            preserve_default=False,
        ),
    ]
