# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remotes', '0008_auto_20150123_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='remote',
            name='key',
            field=models.SlugField(unique=True, max_length=120),
            preserve_default=True,
        ),
    ]
