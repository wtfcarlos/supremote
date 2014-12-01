# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remotes', '0002_remote_owner'),
    ]

    operations = [
        migrations.RenameField(
            model_name='remote',
            old_name='owner',
            new_name='developer',
        ),
    ]
