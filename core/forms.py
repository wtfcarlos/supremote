# -*- coding: utf8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.core.exceptions import ValidationError
from django import forms

from django.contrib.auth.forms import UserCreationForm

from remotes import models as remotes

from django.contrib.auth.models import User


class SignupForm(UserCreationForm):
	class Meta(UserCreationForm.Meta):
		fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

	def __init__(self, *args, **kwargs):
		super(SignupForm, self).__init__(*args, **kwargs)
		for key in self.fields:
			self.fields[key].required = True

	def clean_email(self):
		email = self.cleaned_data.get('email')
		username = self.cleaned_data.get('username')
		if email and User.objects.filter(email=email).exclude(username=username).count():
			raise forms.ValidationError(u'There is already a User with the given email.')
		return email


class RemoteField(forms.Form):
	def __init__(self, *args, **kwargs):

		self.title = kwargs.pop('title')
		self.description = kwargs.pop('description')
		self.initial_value = kwargs.pop('initial')

		super(RemoteField, self).__init__(*args, **kwargs)

class RemoteTextField(RemoteField):

	def __init__(self, *args, **kwargs):
		max_length = kwargs.pop('max_length')

		super(RemoteTextField, self).__init__(*args, **kwargs)
		self.fields['value'] = forms.CharField(
			label = self.title,
			max_length = max_length,
			help_text = self.description,
			initial=self.initial_value
		)

class RemoteNumberRangeField(RemoteField):

	def __init__(self, *args, **kwargs):
		choice_range = kwargs.pop('choice_range')
		super(RemoteNumberRangeField, self).__init__(*args, **kwargs)
		self.fields['value'] = forms.TypedChoiceField(
			label = self.title,
			help_text = self.description,
			choices = [(str(i), str(i)) for i in range(choice_range[0], choice_range[1] + 1)],
			coerce=int,
			initial=self.initial_value
		)

class RemoteBooleanField(RemoteField):

	def __init__(self, *args, **kwargs):
		default_choice = kwargs.pop('default_choice')
		super(RemoteBooleanField, self).__init__(*args, **kwargs)
		self.fields['value'] = forms.BooleanField(
			label=self.title,
			help_text=self.description,
			required=False,
			initial=self.initial_value
		)

class RemoteMultipleField(RemoteField):

	def __init__(self, *args, **kwargs):
		choices = kwargs.pop('choices')
		super(RemoteMultipleField, self).__init__(*args, **kwargs)
		self.fields['value'] = forms.ChoiceField(
			label = self.title,
			help_text= self.description,
			choices = [(s, s) for s in choices],
			initial=self.initial_value
		)


class RemoteCreateForm(forms.ModelForm):
	class Meta:
		model = remotes.Remote
		fields = ['name', 'key', 'endpoint', 'configuration', 'developer']
		widgets = {
			'developer': forms.HiddenInput(),
			'configuration': forms.Textarea(attrs={'class': 'remote-configuration'}),
		}
		help_texts = {
			'name': _('A common name for your remote.'),
			'key': _('A unique key for your remote, containing only letters, numbers, underscores or hyphens. <br /><strong>You will not be able to change it later.</strong>'),
			'endpoint': _('REST endpoint where supremote can POST your server <i>(optional)</i>'),
			'configuration': _('Please refer to the <a href="#">API documentation</a> for details.')
		}


class RemoteEditForm(forms.ModelForm):
	class Meta:
		model = remotes.Remote
		fields = ['name', 'endpoint', 'configuration']

		widgets = {
			'configuration': forms.Textarea(attrs={'class': 'remote-configuration'}),
		}

		help_texts = {
			'name': _('A common name for your remote.'),
			'endpoint': _('REST endpoint where supremote can POST your server'),
			'configuration': _('Please refer to the <a href="#">API documentation</a> for details.'),
		}

class RemoteInvitationSendForm(forms.Form):
	email = forms.EmailField()