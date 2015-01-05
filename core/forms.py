# -*- coding: utf8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django import forms

from remotes import models as remotes

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

		help_texts = {
			'name': _('A common name for your remote.'),
			'configuration': _('Please refer to the <a href="#">API documentation</a> for details.')
		}

class RemoteInvitationSendForm(forms.Form):
	email = forms.EmailField()
