# -*- coding: utf8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.core.exceptions import ValidationError
from django import forms

from django.contrib.auth.forms import UserCreationForm

from remotes import models as remotes

class SignupForm(UserCreationForm):
	class Meta(UserCreationForm.Meta):
		fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')


class RemoteCreateForm(forms.ModelForm):
	class Meta:
		model = remotes.Remote
		fields = ['name', 'key', 'configuration', 'developer']
		widgets = {
			'developer': forms.HiddenInput(),
		}
		help_texts = {
			'name': _('A common name for your remote.'),
			'key': _('This key will be part of your REST API URI.'),
			'configuration': _('Please refer to the <a href="#">API documentation</a> for details.')
		}

class RemoteEditForm(forms.ModelForm):
	class Meta:
		model = remotes.Remote
		fields = ['name', 'configuration']

		widgets = {
			'configuration': forms.Textarea(attrs={'class': 'remote-configuration'})
		}

		help_texts = {
			'name': _('A common name for your remote.'),
			'configuration': _('Please refer to the <a href="#">API documentation</a> for details.')
		}

class RemoteInvitationSendForm(forms.Form):
	email = forms.EmailField()


# # -*- coding: utf8 -*-
# import os
# import json

# from django.db import models
# from django_extensions.db.models import TimeStampedModel
# from django.core.exceptions import ValidationError

# from jsonschema import Draft4Validator

# from users import models as users

# def path_to_schema():
# 	module_dir = os.path.dirname(__file__)
# 	file_path = os.path.join(module_dir, "schema.json")
# 	return file_path

# class Remote(TimeStampedModel):
# 	name = models.CharField(max_length=100)
# 	key = models.SlugField(max_length=120)
# 	developer = models.ForeignKey(users.User, related_name="developer")
# 	configuration = models.TextField()

# 	users = models.ManyToManyField(users.User)


# 	def clean(self):

# 		#Load the JSON schema
# 		schema_file = open(path_to_schema())
# 		schema = json.load(schema_file)

# 		validator = Draft4Validator(schema)
# 		configuration_json = json.loads(self.configuration)
			
# 		validator.validate(configuration_json)
		
# 		return super(Remote, self).clean()