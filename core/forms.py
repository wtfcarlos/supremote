# -*- coding: utf8 -*-
from __future__ import unicode_literals
from django import forms

from remotes import models as remotes

class RemoteCreateForm(forms.ModelForm):
	class Meta:
		model = remotes.Remote
		fields = ['name', 'configuration', 'developer']
		widgets = {
			'developer': forms.HiddenInput(),
		}

