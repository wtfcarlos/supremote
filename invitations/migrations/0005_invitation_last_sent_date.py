# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('invitations', '0004_auto_20150104_1944'),
    ]

    operations = [
        migrations.AddField(
            model_name='invitation',
            name='last_sent_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 5, 2, 19, 47, 811329, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
