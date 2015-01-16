# -*- coding: utf8 -*-
from __future__ import unicode_literals
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django_extensions.db.models import TimeStampedModel

from remotes import models as remotes

class User(TimeStampedModel):
	auth_user = models.ForeignKey(User, unique=True)

	def relevant_remotes(self):
		return remotes.Remote.objects.filter(
			Q(developer=self) |
			Q(users__id=self.pk)
		)

	def __unicode__(self):
		return self.auth_user.__unicode__()