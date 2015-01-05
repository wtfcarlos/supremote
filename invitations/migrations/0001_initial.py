# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('to', models.EmailField(max_length=75)),
                ('nonce', models.CharField(max_length=36)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
