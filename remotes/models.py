# -*- coding: utf8 -*-
import os
import json
import jsonschema
import requests 
import datetime
import hmac
import uuid

from django.db import models
from django.core.cache import get_cache
from django_extensions.db.models import TimeStampedModel
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils import timezone

from jsonschema import Draft4Validator
from encrypted_fields import EncryptedCharField

def path_to_schema():
	module_dir = os.path.dirname(__file__)
	file_path = os.path.join(module_dir, "schema.json")
	return file_path


def get_body_signature(body, secret):
	body_str = json.dumps(body)
	return hmac.new(body_str, secret).hexdigest()

def get_headers(signature):
	return {
		'Content-Type': 'application/json',
		'X-Supremote-Signature': signature
	}

class Remote(TimeStampedModel):
	name = models.CharField(max_length=100)
	key = models.SlugField(max_length=120)
	developer = models.ForeignKey('users.User', related_name="developer")
	endpoint = models.URLField(null=True, blank=True)
	configuration = models.TextField()
	secret = EncryptedCharField(max_length=36)
	users = models.ManyToManyField('users.User')

	def save(self, *args, **kwargs):
		if not self.pk:
			self.secret = uuid.uuid4()

		ret = super(Remote, self).save(*args, **kwargs)

		# Save default values
		configuration_json = json.loads(self.configuration)

		# Get cached values and types
		values = self.get_values()
		types = self.get_types()

		for key, field in configuration_json["fields"].iteritems():
			# If the field is not an action
			if field["type"] != "action":
				# Get the default value and the type as per the JSON conf.
				default_value = field["default"]
				field_type = field["type"]

				# Get the type we have cached, in case the types differ.
				cached_type = types.get(key)

				if cached_type != field_type:
					# If they do differ, set the value to the default value and update the type
					values[key] = default_value
					types[key] = field_type
				else:
					# If they don't, just add the value if the key was not populated.
					cached_value = values.get(key, default_value)
					values[key] = cached_value

		self.save_values(values)
		self.save_types(types)

		return ret

		

	def update_endpoint(self, user_email):
		values = self.get_values()
		
		request_body = {
			'user': user_email,
			'remote_key': self.key,
			'data': values
		}

		signature = get_body_signature(request_body, self.secret)

		response = requests.post(
			self.endpoint,
			data=json.dumps(request_body),
			headers=get_headers(signature)
		)

		print response

	def trigger_action(self, action_name, user_email):
		configuration = self.get_configuration()
		action_dictionary = configuration['fields'].get(action_name)

		if action_dictionary:
			endpoint = action_dictionary['endpoint']
			throttle = action_dictionary['throttle']
			throttle_threshold = timezone.now() - datetime.timedelta(seconds=throttle)

			# Look for latest throttle entry for this action.
			throttle_entry_count = ActionThrottle.objects.filter(
				remote = self,
				key = action_name,
				created__gt = throttle_threshold,
				status_code = 200,
			).count()
			
			if throttle_entry_count == 0:
				# Action must be triggered.
				request_body = {
					'user': user_email,
					'remote_key': self.key,
					'data': {
						'action_id': action_name,
						'triggered': str(timezone.now()),
					}
				}

				signature = get_body_signature(request_body, self.secret)
				headers = get_headers(signature)

				response = requests.post(
					endpoint,
					data=json.dumps(request_body),
					headers=headers
				)

				ActionThrottle(
					remote=self,
					key = action_name,
					status_code=response.status_code
				).save()
				return True
			else:
				# Action is throttled and must not be carried on.
				return False
		else:
			raise KeyError("%s is not an action defined by this remote." % action_name)

	def get_configuration(self):
		return json.loads(self.configuration)

	def get_types(self):
		cache = get_cache('default')
		key = self.get_type_cache_key()
		return cache.get(key, {})

	def save_types(self, types):
		cache = get_cache('default')
		key = self.get_type_cache_key()
		cache.set(key, types, None)

	def get_values(self):
		cache = get_cache('default')
		key = self.get_cache_key()
		return cache.get(key, {})

	def save_values(self, values):
		cache = get_cache('default')
		key = self.get_cache_key()
		cache.set(key, values, None)

	def save_default(self, key, field):
		# Saves the default value for this key if the key does not have an associated value.
		values = self.get_values()
		default_value = field["default"]
		cached_value = values.get(key, default_value)
		values[key] = cached_value
		self.save_values(values)

	def get_cache_key(self):
		return 'remote-{}-{}'.format(self.pk, self.key)

	def get_type_cache_key(self):
		return 'type-remote-{}-{}'.format(self.pk, self.key)

	def get_absolute_url(self):
		return reverse('core:remote_detail', kwargs={
			'remote_id': self.pk,
			'remote_key': self.key,
		})

	def clean(self):

		#Load the JSON schema
		schema_file = open(path_to_schema())
		schema = self.validate_schema(schema_file)
		configuration_json = self.validate_configuration(schema, self.configuration)
		schema_file.close()
		return super(Remote, self).clean()

	def validate_schema(self, schema_file):
		try:
			schema = json.load(schema_file)
		except:
			raise ValidationError("Schema appears to be invalid.")
		return schema

	def validate_configuration(self, schema, configuration):

		validator = Draft4Validator(schema)
		try:
			configuration_json = json.loads(self.configuration)
		except:
			raise ValidationError("The configuration JSON provided is not valid.")

		try:
			validator.validate(configuration_json)
		except jsonschema.exceptions.ValidationError as e:
			full_error_path = '.'.join(list(e.absolute_path))
			error_message = "There is a problem with the entry {}.".format(full_error_path)
			raise ValidationError(error_message)

		for key, field in configuration_json["fields"].iteritems():
			self.validate_field(key, field)

		return configuration_json


	def validate_field(self, key, field):

		acceptable_action_classes = ['danger', 'primary', 'default', 'warning', 'success', 'info']

		if field["type"] == "text":
			if field["max-length"] <= 0:
				raise ValidationError("{}: max-length must be greater than 0.".format(key))
			if len(field["default"]) > field["max-length"]:
				raise ValidationError("{}: default value is longer than max-length".format(key))

		elif field["type"] == "number":
			f_range = field["range"]
			if f_range[0] >= f_range[1]:
				raise ValidationError("{}: range must be [lower, upper]".format(key))

			if field["default"] not in range(f_range[0], f_range[1]+1):
				raise ValidationError("{}: default value is not in range {}".format(key, f_range))

		elif field["type"] == "multiple":
			if field["default"] not in field["choices"]:
				raise ValidationError("{}: default value is not in {}".format(key, field["choices"]))

		elif field["type"] == "action":
			if not field["endpoint"].startswith("http"):
				raise ValidationError("{}: endpoint must start with http or https.".format(key))

			if not field["class"] in acceptable_action_classes:
				raise ValidationError("{}: class must be one of {}".format(key, acceptable_action_classes))


	def __unicode__(self):
		return self.name

	def get_pending_invitations(self):
		return self.invitation_set.filter(
			remote=self,
			accepted=False,
			declined=False
		)

class ActionThrottle(TimeStampedModel):
	remote = models.ForeignKey(Remote)
	key = models.CharField(max_length=200)
	status_code = models.PositiveSmallIntegerField()