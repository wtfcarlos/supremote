# -*- coding: utf8 -*-
import os
import json
import jsonschema
import grequests 
import datetime
import hmac
import hashlib
import uuid

from django.db import models
from django.core.cache import get_cache
from django_extensions.db.models import TimeStampedModel
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import URLValidator, RegexValidator
from django.utils import timezone

from jsonschema import Draft4Validator
from encrypted_fields import EncryptedCharField

from django_redis import get_redis_connection

def path_to_schema():
	module_dir = os.path.dirname(__file__)
	file_path = os.path.join(module_dir, "schema.json")
	return file_path


def default_config_json():
	return """{
   "fieldsets":[
      {
         "title":"Example Fieldset",

         "fields":[
            "exampleTextInput",
            "exampleBooleanInput"
         ],

         "helpText":"Your fieldset's description is optional and goes here."
      }
   ],

   "fields":{

      "exampleTextInput":{
         "type":"text",
         "title":"Example Text",
         "description":"An example text inupt",
         "default":"Supremote rocks!",
         "maxLength":30
      },

      "exampleBooleanInput":{
         "type":"boolean",
         "title":"Example Boolean Input",
         "description":"It's rendered as a checkbox on web and as a switch on iOS",
         "default":false
      }

   }
}
	"""

def get_body_signature(body, secret, transaction_id):
	body_str = json.dumps(body)
	signature_maker = hmac.new(str(secret), '', hashlib.sha1)
	signature_maker.update(body_str)
	signature_maker.update(str(transaction_id))
	return signature_maker.hexdigest()

def get_headers(signature, transaction_id):
	return {
		'Content-Type': 'application/json',
		'X-Supremote-Signature': signature,
		'X-Supremote-Transaction-Id': str(transaction_id),
		'User-Agent': 'Supremote/1.0'
	}


class SocketOrigin(TimeStampedModel):
	remote = models.ForeignKey('Remote')
	domain = models.CharField(
		max_length=255,
		validators = [
			RegexValidator(
				r'^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$',
				'Only valid domain names are allowed. No whitespace either.',
				'This domain name looks invalid.'
			)
		]
	)

	def save(self, *args, **kwargs):
		if not self.pk:
			conn = get_redis_connection('default')
			conn.sadd(self.remote.get_domains_key(), self.domain)
		return super(SocketOrigin, self).save(*args, **kwargs)

	def delete(self):
		conn = get_redis_connection('default')
		conn.srem(self.remote.get_domains_key(), self.domain)
		super(SocketOrigin, self).delete()

	class Meta:
		unique_together = (('remote', 'domain',),)



class Remote(TimeStampedModel):
	name = models.CharField(max_length=100)
	key = models.SlugField(max_length=120, unique=True)
	developer = models.ForeignKey('users.User', related_name="developer")
	endpoint = models.URLField(null=True, blank=True)
	configuration = models.TextField(default=default_config_json())
	secret = EncryptedCharField(max_length=36)
	users = models.ManyToManyField('users.User')

	allow_all_origins = models.BooleanField(default=False, verbose_name="Development mode enabled")

	def save(self, *args, **kwargs):
		if not self.pk:
			self.secret = uuid.uuid4()

		conn = get_redis_connection('default')
		conn.set(self.get_allow_all_key(), int(self.allow_all_origins))

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

	def emit_socket_event(self, event_type, action_name=None):
		socket_emit_url = 'http://localhost:9000/emit/'
		emit_password = os.environ['SUPREMOTE_SOCKET_KEY']

		request_body = {
			'event_type': event_type,
			'room': self.key,
			'message': self.get_values(),
			'password': emit_password
		}

		if action_name:
			request_body.update({'action_name': action_name})

		grequests.post(
			socket_emit_url,
			data=json.dumps(request_body),
			headers={'Content-Type': 'application/json'}
		).send()

	def update_endpoint(self, user_email):
		self.emit_socket_event('update')

		if self.endpoint:
			values = self.get_values()
			
			request_body = {
				'user': user_email,
				'remote_key': self.key,
				'data': values,
				'updated': str(timezone.now()),
			}

			transaction_id = uuid.uuid4()
			signature = get_body_signature(request_body, self.secret, transaction_id)

			r = grequests.post(
				self.endpoint,
				data=json.dumps(request_body),
				headers=get_headers(signature, transaction_id)
			).send()

	def trigger_action(self, action_name, user_email):
		configuration = self.get_configuration()
		action_dictionary = configuration['fields'].get(action_name)

		if action_dictionary:
			endpoint = action_dictionary.get('endpoint') or self.endpoint or None
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
				self.emit_socket_event('action', action_name=action_name)
				if endpoint:
					# Action must be triggered.
					request_body = {
						'user': user_email,
						'remote_key': self.key,
						'data': {
							'action_id': action_name,
							'triggered': str(timezone.now()),
						}
					}

					transaction_id = uuid.uuid4()
					signature = get_body_signature(request_body, self.secret, transaction_id)
					headers = get_headers(signature, transaction_id)

					grequests.post(
						endpoint,
						data=json.dumps(request_body),
						headers=headers
					).send()

				# FIXME: Put actual response status code.
				ActionThrottle(
					remote=self,
					key = action_name,
					status_code=200
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
		return '{}.values'.format(self.key)

	def get_type_cache_key(self):
		return '{}.types'.format(self.key)

	def get_domains_key(self):
		return '{}.domains'.format(self.key)

	def get_allow_all_key(self):
		return '{}.allow_all_origins'.format(self.key)

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
			raise ValidationError(e)

		for key, field in configuration_json["fields"].iteritems():
			self.validate_field(key, field)

		index = 0
		fieldset_entries = []

		for fieldset in configuration_json["fieldsets"]:
			for field in fieldset["fields"]:
				if field not in fieldset_entries:
					fieldset_entries.append(field)
				else:
					raise ValidationError("Fieldset at index {} repeats field key '{}'.".format(index, field))

				if field not in configuration_json["fields"]:
					raise ValidationError("The key '{}'' is not defined as a field in fieldset at index {}".format(field, index))

			index += 1



		return configuration_json


	def validate_field(self, key, field):

		acceptable_action_classes = ['danger', 'primary', 'default', 'warning', 'success', 'info']

		if field["type"] == "text":
			if field["maxLength"] <= 0:
				raise ValidationError("{}: maxLength must be greater than 0.".format(key))
			if len(field["default"]) > field["maxLength"]:
				raise ValidationError("{}: default value is longer than maxLength".format(key))

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
			endpoint = field.get("endpoint")

			if endpoint:
				validator = URLValidator()
				validator.schemes = ["http", "https"]
				validator(field["endpoint"])

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