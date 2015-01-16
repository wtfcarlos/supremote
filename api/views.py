# -*- coding: utf8 -*-
from __future__ import unicode_literals, division

from django.contrib.auth.models import User

import json
from collections import OrderedDict

from users import models as users
from remotes import models as remotes
from rest_framework.views import APIView
from rest_framework import serializers, viewsets, generics
from rest_framework.response import Response

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ['username', 'email', 'first_name', 'last_name']

class AppUserSerializer(serializers.ModelSerializer):
	auth_user = UserSerializer()
	class Meta:
		model = users.User
		fields = ['id', 'auth_user']

class RemoteSerializer(serializers.ModelSerializer):
	developer = AppUserSerializer()
	class Meta:
		model = remotes.Remote
		fields = ['id', 'name', 'key', 'developer']

class RemoteDetailSerializer(serializers.ModelSerializer):
	developer = AppUserSerializer()
	class Meta:
		model = remotes.Remote
		fields = ['id', 'name', 'key', 'developer', 'configuration']

	def to_representation(self, obj):
		remote_repr = super(RemoteDetailSerializer, self).to_representation(obj)

		remote_repr['configuration'] = json.loads(
			remote_repr['configuration'],
			object_pairs_hook=OrderedDict
		)

		print obj.get_values()

		remote_repr['current_values'] = obj.get_values()

		return remote_repr

class ProfileView(generics.RetrieveAPIView):
	serializer_class = UserSerializer
	model = User

	def get_object(self):
		return self.request.user

class RemoteListView(generics.ListAPIView):
	serializer_class = RemoteSerializer
	model = remotes.Remote

	def get_queryset(self):
		app_user = users.User.objects.get(auth_user=self.request.user)
		return app_user.relevant_remotes()

class RetrieveRemoteView(generics.RetrieveAPIView):
	serializer_class = RemoteDetailSerializer
	model = remotes.Remote

	def get_object(self):
		return remotes.Remote.objects.get(
			pk=self.kwargs['remote_id']
		)

class JSONRequestBodyView(APIView):
	def post(self, request, format=None):
		try:
			self.request_json = json.loads(request.body)
		except:
			return Response(
				status = 500,
				data = {'error': 'Invalid JSON Given'}
			)

class RemoteTriggerActionView(JSONRequestBodyView):
	def post(self, request, format=None):
		super(RemoteTriggerActionView, self).post(request, format)
		remote_pk = self.request_json['remote_id']
		app_user = users.User.objects.get(auth_user=request.user)
		action_id = self.request_json['action_id']
		remote = remotes.Remote.objects.get(pk=remote_pk)

		if remote in app_user.relevant_remotes():
			try:
				if remote.trigger_action(action_id, request.user.email):
					return Response(status=200, data={'message': 'The action has been performed.'})
				else:
					return Response(status=400, data={'error': 'It is too soon to perform the action!'})
			except KeyError as ex:
				return Response(status=400, data={'error': ex.message})
		else:
			return Response(status=403)



class RemoteValuesChangeView(JSONRequestBodyView):
	def post(self, request, format=None):
		super(RemoteValuesChangeView, self).post(request, format)
		remote_pk = self.request_json['remote_id']
		app_user = users.User.objects.get(auth_user=request.user)
		remote = remotes.Remote.objects.get(pk=remote_pk)

		if remote in app_user.relevant_remotes():
			old_values = remote.get_values()
			new_values = self.request_json['values']
			for key, value in new_values.iteritems():
				if key in old_values:
					# TODO: Enforce types
					old_values[key] = value
				else:
					return Response(status=400, data={'error': 'Key {} is not expected by Remote.'.format(key)})
			remote.save_values(old_values)
			remote.update_endpoint(request.user.email)
			return Response(status=200, data={'response': 'OK'})
		else:
			return Response(status=403)
