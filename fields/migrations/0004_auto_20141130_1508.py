# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remotes', '0001_initial'),
        ('fields', '0003_auto_20141130_1444'),
    ]

    operations = [
        migrations.AddField(
            model_name='booleanfield',
            name='remote',
            field=models.ForeignKey(default=1, to='remotes.Remote'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='multiplechoicefield',
            name='remote',
            field=models.ForeignKey(default=1, to='remotes.Remote'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='numberchoicefield',
            name='remote',
            field=models.ForeignKey(default=1, to='remotes.Remote'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='textfield',
            name='remote',
            field=models.ForeignKey(default=1, to='remotes.Remote'),
            preserve_default=False,
        ),
    ]
