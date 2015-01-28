# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('remotes', '0007_auto_20150123_1519'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='socketorigin',
            options={},
        ),
        migrations.AlterField(
            model_name='socketorigin',
            name='domain',
            field=models.CharField(max_length=255, validators=[django.core.validators.RegexValidator(b'^([a-z0-9]+(-[a-z0-9]+)*\\.)+[a-z]{2,}$', b'Only valid domain names are allowed. No whitespace either.', b'This domain name looks invalid.')]),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='socketorigin',
            unique_together=set([('remote', 'domain')]),
        ),
    ]
