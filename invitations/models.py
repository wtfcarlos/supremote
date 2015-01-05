# -*- coding: utf8 -*-
from django.db import models
from django.core.urlresolvers import reverse
from django_extensions.db.models import TimeStampedModel
import uuid

class Invitation(TimeStampedModel):
	to = models.EmailField()
	nonce = models.CharField(max_length=36)
	accepted = models.BooleanField(default=False)

	def get_absolute_url(self):
		return reverse('core:invitation_link', kwargs={
			'nonce': self.nonce
		})


	def save(self, *args, **kwargs):
		if self.pk is None:
			self.nonce = uuid.uuid4()
		return super(Invitation, self).save(*args, **kwargs)