# -*- coding: utf8 -*-
from django.db import models
from django_extensions.db.models import TimeStampedModel

from users import models as users

class Remote(TimeStampedModel):
	name = models.CharField(max_length=100)
	developer = models.ForeignKey(users.Developer)
	configuration = models.TextField()

	def __unicode__(self):
		return self.name