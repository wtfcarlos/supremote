# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fields', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='multiplechoicefield',
            name='value',
            field=models.ForeignKey(to='fields.TextChoice', null=True),
            preserve_default=True,
        ),
    ]
