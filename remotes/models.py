# -*- coding: utf8 -*-
import os
import json

from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.core.exceptions import ValidationError

import jsonschema
from jsonschema import Draft4Validator

from users import models as users

def path_to_schema():
	module_dir = os.path.dirname(__file__)
	file_path = os.path.join(module_dir, "schema.json")
	return file_path

class Remote(TimeStampedModel):
	name = models.CharField(max_length=100)
	key = models.SlugField(max_length=120)
	developer = models.ForeignKey(users.User, related_name="developer")
	configuration = models.TextField()

	users = models.ManyToManyField(users.User)


	def clean(self):

		#Load the JSON schema
		schema_file = open(path_to_schema())
		schema = json.load(schema_file)

		validator = Draft4Validator(schema)
		configuration_json = json.loads(self.configuration)

		try:
			validator.validate(configuration_json)
		except jsonschema.exceptions.ValidationError as e:
			raise ValidationError(e.message)

		return super(Remote, self).clean()

	def __unicode__(self):
		return self.name

	def get_pending_invitations(self):
		return self.invitation_set.filter(
			remote=self,
			accepted=False,
			declined=False
		)