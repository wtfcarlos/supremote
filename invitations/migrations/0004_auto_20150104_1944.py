# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invitations', '0003_invitation_remote'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='invitation',
            options={},
        ),
        migrations.AlterUniqueTogether(
            name='invitation',
            unique_together=set([('to', 'remote')]),
        ),
    ]
