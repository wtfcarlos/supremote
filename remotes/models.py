# -*- coding: utf8 -*-
from django.db import models
from django_extensions.db.models import TimeStampedModel

from users import models as users

class Remote(TimeStampedModel):
	name = models.CharField(max_length=100)
	key = models.SlugField(max_length=120)
	developer = models.ForeignKey(users.User, related_name="developer")
	configuration = models.TextField()

	users = models.ManyToManyField(users.User)

	def __unicode__(self):
		return self.name

	def get_pending_invitations(self):
		return self.invitation_set.filter(
			remote=self,
			accepted=False,
			declined=False
		)