# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django.core.validators
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('remotes', '0006_remote_secret'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocketOrigin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('domain', models.CharField(max_length=255, validators=[django.core.validators.RegexValidator(b'^([a-z0-9]+(-[a-z0-9]+)*\\.)+[a-z]{2,}$', b'Only valid domain names are allowed', b'This domain name looks invalid.')])),
                ('remote', models.ForeignKey(to='remotes.Remote')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='remote',
            name='allow_all_origins',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
