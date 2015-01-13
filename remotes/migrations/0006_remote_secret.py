# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import encrypted_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('remotes', '0005_actionthrottle_status_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='remote',
            name='secret',
            field=encrypted_fields.fields.EncryptedCharField(default='36183cc6-8ae5-446c-8a2f-379b3d286400', max_length=36),
            preserve_default=False,
        ),
    ]
