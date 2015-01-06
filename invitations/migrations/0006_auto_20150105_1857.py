# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invitations', '0005_invitation_last_sent_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='invitation',
            name='declined',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='invitation',
            name='finalized_date',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='invitation',
            name='last_sent_date',
            field=models.DateTimeField(auto_now_add=True),
            preserve_default=True,
        ),
    ]
