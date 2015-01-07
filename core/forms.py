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