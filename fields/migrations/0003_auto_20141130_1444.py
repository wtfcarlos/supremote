# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fields', '0002_auto_20141130_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='multiplechoicefield',
            name='value',
            field=models.ForeignKey(blank=True, to='fields.TextChoice', null=True),
            preserve_default=True,
        ),
    ]
