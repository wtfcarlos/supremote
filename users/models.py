# -*- coding: utf8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django_extensions.db.models import TimeStampedModel

class Developer(TimeStampedModel):
	auth_user = models.ForeignKey(User, unique=True)

	def __unicode__(self):
		return '{} - Developer'.format(self.auth_user)