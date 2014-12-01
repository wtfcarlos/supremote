# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fields', '0004_auto_20141130_1508'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booleanfield',
            name='value',
            field=models.BooleanField(default=None),
            preserve_default=True,
        ),
    ]
