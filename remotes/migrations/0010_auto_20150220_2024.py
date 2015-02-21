# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remotes', '0009_auto_20150127_2110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='remote',
            name='allow_all_origins',
            field=models.BooleanField(default=False, verbose_name=b'Development mode enabled'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='remote',
            name='configuration',
            field=models.TextField(default=b'{\n   "fieldsets":[\n      {\n         "title":"Example Fieldset",\n\n         "fields":[\n            "exampleTextInput",\n            "exampleBooleanInput"\n         ],\n\n         "helpText":"Your fieldset\'s description is optional and goes here."\n      }\n   ],\n\n   "fields":{\n\n      "exampleTextInput":{\n         "type":"text",\n         "title":"Example Text",\n         "description":"An example text inupt",\n         "default":"Supremote rocks!",\n         "maxLength":30\n      },\n\n      "exampleBooleanInput":{\n         "type":"boolean",\n         "title":"Example Boolean Input",\n         "description":"It\'s rendered as a checkbox on web and as a switch on iOS",\n         "default":false\n      }\n\n   }\n}\n\t'),
            preserve_default=True,
        ),
    ]
