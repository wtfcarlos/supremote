# -*- coding: utf8 -*-
from __future__ import unicode_literals
from django.db import models
from django_extensions.db.models import TimeStampedModel

from remotes import models as remotes

class AbstractBaseField(TimeStampedModel):
	key = models.CharField(max_length=100)
	remote = models.ForeignKey(remotes.Remote)

	class Meta:
		abstract = True

	def __unicode__(self):
		return self.value

class TextField(AbstractBaseField):
	value = models.CharField(max_length=140)

class MultipleChoiceField(AbstractBaseField):
	value = models.ForeignKey("TextChoice", blank=True, null=True)

	def __unicode__(self):
		if self.value:
			return self.value.__unicode__()
		return 'None'

class TextChoice(models.Model):
	field = models.ForeignKey(MultipleChoiceField)
	value = models.CharField(max_length=50)

	def __unicode__(self):
		return self.value

class BooleanField(AbstractBaseField):
	value = models.BooleanField(default=None)
	default = models.BooleanField(default=False)

	def __unicode__(self):
		return '{}'.format(self.value)

class NumberChoiceField(AbstractBaseField):
	lower = models.SmallIntegerField(default=1)
	upper = models.SmallIntegerField(default=10)
	value = models.SmallIntegerField(default=5)

	def __unicode__(self):
		return '{}'.format(self.value)







