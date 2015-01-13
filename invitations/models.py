# -*- coding: utf8 -*-
from django.db import models
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.core.mail import send_mail, EmailMessage
from django_extensions.db.models import TimeStampedModel
from remotes import models as remotes

from users import models as users

import uuid

class Invitation(TimeStampedModel):
	to = models.EmailField()
	nonce = models.CharField(max_length=36)
	remote = models.ForeignKey(remotes.Remote)
	accepted = models.BooleanField(default=False)
	declined = models.BooleanField(default=False)
	finalized_date = models.DateTimeField(null=True)
	last_sent_date = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = (('to', 'remote'), )

	def decline(self):
		self.finalized_date = timezone.now()
		self.declined = True
		self.accepted = False
		self.save()
		self.delete()

	def accept(self):
		# Automatically assigns the user to the remote.
		user = users.User.objects.get(auth_user__email=self.to)
		self.accepted = True
		self.declined = False
		self.finalized_date = timezone.now()
		self.remote.users.add(user)
		self.save()
		self.delete()


	def get_absolute_url(self):
		return reverse('core:invitation_link', kwargs={
			'nonce': self.nonce
		})

	def send_email(self):
		self.last_sent_date = timezone.now()
		self.save()
		message = EmailMessage(
			subject="Supremote Invitation",
			from_email="noreply@supremote.com",
			to=[self.to,]
		)

		message.body = "You have been invited to a supremote!\nPlease follow this link: http://localhost:8111{}".format(self.get_absolute_url())
		
		message.send()


	def save(self, *args, **kwargs):
		if self.pk is None:
			self.nonce = uuid.uuid4()
		return super(Invitation, self).save(*args, **kwargs)