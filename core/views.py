# -*- coding: utf8 -*-
from __future__ import unicode_literals
from django.views import generic
from django.core.urlresolvers import reverse_lazy, reverse
from django.core.exceptions import ValidationError
from django.core.mail import send_mail, EmailMessage
from django.core.cache import get_cache
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import PasswordChangeForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseForbidden, HttpResponse
from django.utils import timezone
from braces.views import LoginRequiredMixin, UserPassesTestMixin

from rest_framework.authtoken.models import Token

import json
import hashlib
import collections
import datetime

from users import models as users
from fields import models as fields
from remotes import models as remotes
from invitations import models as invitations

from . import forms
from . import util

@csrf_exempt
def TestActionReceiveView(request):
	import hmac
	remote_secret = '32365bf6-b25d-4be1-968b-d51c23a4a02f'

	print 'REQUEST SIGNATURE: {}'.format(request.META['HTTP_X_SUPREMOTE_SIGNATURE'])
	print 'TRANSACTION ID: {}'.format(request.META['HTTP_X_SUPREMOTE_TRANSACTION_ID'])
	
	transaction_id = request.META['HTTP_X_SUPREMOTE_TRANSACTION_ID']

	signature_maker = hmac.new(str(remote_secret), '', hashlib.sha1)
	signature_maker.update(request.body)
	signature_maker.update(transaction_id)

	print 'CALCULATED SIGNATURE: {}'.format(
		signature_maker.hexdigest()
	)

	return HttpResponse()

@csrf_exempt
def TestEndpointProcessView(request):
	import hmac
	remote_secret = '32365bf6-b25d-4be1-968b-d51c23a4a02f'

	print 'REQUEST SIGNATURE: {}'.format(request.META['HTTP_X_SUPREMOTE_SIGNATURE'])
	print 'TRANSACTION ID: {}'.format(request.META['HTTP_X_SUPREMOTE_TRANSACTION_ID'])
	
	transaction_id = request.META['HTTP_X_SUPREMOTE_TRANSACTION_ID']

	signature_maker = hmac.new(str(remote_secret), '', hashlib.sha1)
	signature_maker.update(request.body)
	signature_maker.update(transaction_id)

	print 'CALCULATED SIGNATURE: {}'.format(
		signature_maker.hexdigest()
	)

	return HttpResponse()


class TermsAndConditionsView(generic.TemplateView):
	template_name = "core/terms.html"

class PrivacyView(generic.TemplateView):
	template_name = "core/privacy.html"

class SupremoteLoginRequiredMixin(LoginRequiredMixin):
	login_url = reverse_lazy("core:index")

class AuthorizedRemoteLoginRequiredMixin(LoginRequiredMixin):

	def get_app_user(self, user):
		app_user = users.User.objects.get(auth_user=user)
		return app_user

	def get_remote(self):
		# Override if necessary.
		return self.get_object()

	def dispatch(self, request, *args, **kwargs):
		app_user = self.get_app_user(request.user)
		remote = self.get_remote()
		if app_user in remote.users.all() or app_user == remote.developer:
			return super(AuthorizedRemoteLoginRequiredMixin, self).dispatch(request, *args, **kwargs)
		else:
			return HttpResponseForbidden()

class RedirectIfLoggedInViewMixin(object):

	def get(self, request, *args, **kwargs):
		if request.user.is_authenticated():
			return redirect(reverse('core:remote_list'))
		return super(RedirectIfLoggedInViewMixin, self).get(request, *args, **kwargs)

class SignupView(RedirectIfLoggedInViewMixin, generic.FormView):
	template_name = "core/signup.html"
	form_class = forms.SignupForm
	success_url = reverse_lazy('core:remote_list')

	def form_valid(self, form):

		signup_password = form.cleaned_data['password1']
		email = form.cleaned_data['email']

		user_count = users.User.objects.filter(
				auth_user__email = email
		).count()

		if user_count == 0:
			user = form.save()
			user = authenticate(username=user.username, password=signup_password)
			app_user = users.User(auth_user=user)
			Token(user=user).save()
			app_user.save()
			login(self.request, user)
		else:
			raise ValidationError("There is already a User with the given email.")

		
		return super(SignupView, self).form_valid(form)				

class IndexView(RedirectIfLoggedInViewMixin, generic.FormView):

	template_name = "core/index.html"

	def get_form(self, form_class):
		return AuthenticationForm(self.request, self.request.POST or None)

	def form_valid(self, form):
		user = form.get_user()
		login(self.request, user)

		if 'next' in self.request.GET:
			self.success_url = self.request.GET['next']
		else:
			self.success_url = reverse('core:remote_list')

		return super(IndexView, self).form_valid(form)

class InvitationAcceptView(SupremoteLoginRequiredMixin, generic.TemplateView):
	template_name = "core/invitation_confirm.html"

	def dispatch(self, request, *args, **kwargs):

		invitation_nonce = kwargs.pop('nonce')

		self.invitation = get_object_or_404(invitations.Invitation, nonce=invitation_nonce)

		return super(InvitationAcceptView, self).dispatch(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):

		if 'action' in request.POST:
			if request.POST['action'] == 'accept':
				# Accept
				self.invitation.accept()
			elif request.POST['action'] == 'decline':
				# Decline
				self.invitation.decline()
				pass

		return redirect('core:remote_list')

	def get_context_data(self, **kwargs):
		context = super(InvitationAcceptView, self).get_context_data(**kwargs)

		if self.request.user.email == self.invitation.to:
			context['remote'] = self.invitation.remote
			context['correct_email'] = True
		else:
			context['correct_email'] = False

		return context


class AccountSettingsView(SupremoteLoginRequiredMixin, generic.FormView):
	template_name = 'core/account_settings.html'
	success_url = reverse_lazy('core:account_settings')

	def get_form(self, form_class):
		return PasswordChangeForm(self.request.user, self.request.POST or None)

	def form_valid(self, form):

		form.save()

		try:
			auth_token = Token.objects.get(user=self.request.user)
			auth_token.delete()
		except Token.DoesNotExist:
			pass
		
		Token.objects.create(user=self.request.user)


		messages.success(self.request, "Your password was changed successfuly.")

		return super(AccountSettingsView, self).form_valid(form)

class ResendInvitationView(SupremoteLoginRequiredMixin, generic.RedirectView):

	permanent = False

	def get(self, request, *args, **kwargs):
		# TODO - throttle
		invitation_id = kwargs.pop('invitation_id')

		self.invitation = get_object_or_404(invitations.Invitation, pk=invitation_id)

		if self.invitation.remote.developer.auth_user == self.request.user:
			self.invitation.send_email()

			messages.info(self.request, 'The invitation has been resent.')
			return super(ResendInvitationView, self).get(request, *args, **kwargs)
		else:
			return HttpResponseForbidden()

	def get_redirect_url(self, *args, **kwargs):
		return reverse('core:remote_manage_users', kwargs={
			'remote_id': self.invitation.remote.pk,
			'remote_key': self.invitation.remote.key,
		})


class RemoteTriggerActionView(AuthorizedRemoteLoginRequiredMixin, generic.detail.DetailView):
	model = remotes.Remote
	pk_url_kwarg = 'remote_id'
	context_object_name = 'remote'

	def post(self, request, *args, **kwargs):
		# Receive action by name
		prefix = 'remote-action-'
		action_id = request.POST['action_id']
		action_id = action_id[len(prefix):]
		remote = self.get_object()

		try:
			if remote.trigger_action(action_id, request.user.email):
				messages.success(request, "The action has been performed.")
			else:
				messages.error(request, "It is too soon to perform the action!")
		except KeyError as e:
			messages.error(request, e.message)

		return redirect(reverse('core:remote_detail', kwargs=kwargs))





class ManageRemoteOriginsView(AuthorizedRemoteLoginRequiredMixin, generic.detail.SingleObjectMixin, generic.FormView):
	
	template_name = "core/remote_manage_origins.html"
	model = remotes.Remote
	pk_url_kwarg = 'remote_id'
	context_object_name = 'remote'
	form_class = forms.AllowedOriginCreateForm

	success_url = reverse_lazy('core:remote_manage_origins')

	def get_initial(self):
		return {
			'remote': self.object
		}

	def form_valid(self, form):

		if self.object == form.cleaned_data['remote']:
			form.save()
			messages.success(self.request, "The domain has been added.")
		else:
			return HttpResponse(status=401)
		return super(ManageRemoteOriginsView, self).form_valid(form)

	def dispatch(self, request, *args, **kwargs):
		self.object = self.get_object()
		return super(ManageRemoteOriginsView, self).dispatch(request, *args, **kwargs)

	def get_success_url(self):
		return reverse_lazy(
			'core:remote_manage_origins',
			kwargs=self.kwargs
		)

class RemoteFieldItem(object):
	item_type = 'form'
	field = None
	key = None

	def __init__(self, item_type='form', field=None, key=None):
		self.item_type = item_type
		self.field = field
		self.key = key

class RemoteFieldSetItem(object):
	def __init__(self, title, help_text):
		self.fields = []
		self.title = title
		self.help_text = help_text

class RemoteDetailView(AuthorizedRemoteLoginRequiredMixin, generic.detail.DetailView):
	template_name = "core/remote_view.html"

	model = remotes.Remote
	pk_url_kwarg = 'remote_id'
	context_object_name = 'remote'



	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		self.get_context_data(object=self.object)

		remote_cache = self.object.get_values()

		if all([form.is_valid() for form in self.remote_field_forms]):
			for form in self.remote_field_forms:
				key = form.prefix
				value = form.cleaned_data['value']
				remote_cache[key] = value
			self.object.save_values(remote_cache)
			self.object.update_endpoint(request.user.email)
			return redirect(reverse('core:remote_detail', kwargs=kwargs))
		else:
			messages.error(request, 'There was a problem with some of the data you provided. Double-check it and submit again.')
			return super(RemoteDetailView, self).get(request, *args, **kwargs)


	def get_context_data(self, **kwargs):
		context = super(RemoteDetailView, self).get_context_data(**kwargs)

		remote_cache = self.object.get_values()
		ordered_conf = json.loads(self.object.configuration, object_pairs_hook=collections.OrderedDict)

		self.remote_field_keys = [s for s in ordered_conf['fields'].keys() if ordered_conf['fields'][s]['type'] != 'action']

		remote_field_forms = []
		remote_field_dict = {}

		# Process each field's configuration and create the RemoteFieldItems
		for key, field in ordered_conf['fields'].iteritems():
			if field['type'] == 'action':
				field_type = 'action'
				field_form = field
			else:
				field_type = 'form'
				field_form = util.RemoteFieldFactory.create(key, field, self.request.POST or None, remote_cache)
				remote_field_forms.append(field_form)

			item = RemoteFieldItem(field=field_form, item_type=field_type, key=key)
			remote_field_dict.update({key: item})
			

		remote_fieldset_list = []
		for fieldset in ordered_conf["fieldsets"]:
			# For each fieldset, iterate over the elements and add them to a RemoteFieldSetItem
			fieldset_item = RemoteFieldSetItem(fieldset["title"], fieldset.get("helpText"))
			for field_name in fieldset["fields"]:
				fieldset_item.fields.append(remote_field_dict[field_name])

			remote_fieldset_list.append(fieldset_item)


		self.remote_field_forms = remote_field_forms

		context['remote_fieldset_list'] = remote_fieldset_list


		return context

class ManageUsersRemoteView(SupremoteLoginRequiredMixin, generic.detail.SingleObjectMixin, generic.FormView):

	template_name = "core/remote_manage_users.html"

	model = remotes.Remote
	pk_url_kwarg = 'remote_id'
	context_object_name = 'remote'

	form_class = forms.RemoteInvitationSendForm

	def dispatch(self, request, *args, **kwargs):
		self.object = self.get_object()
		return super(ManageUsersRemoteView, self).dispatch(request, *args, **kwargs)


	def form_valid(self, form):
		email = form.cleaned_data['email']
		invitation, created = invitations.Invitation.objects.get_or_create(
			to=email,
			remote=self.object
		)
		if created:
			invitation.save()
			invitation.send_email()
			messages.success(self.request, 'The invitation has been sent.')
		else:
			invitation.send_email()
			messages.info(self.request, 'The invitation has been resent.')

		return super(ManageUsersRemoteView, self).form_valid(form)

	def get_success_url(self):
		return reverse_lazy(
			'core:remote_manage_users',
			kwargs=self.kwargs
		)

class RemoteListView(SupremoteLoginRequiredMixin, generic.TemplateView):
	template_name = "core/remote_list.html"
	model = remotes.Remote

	def get_context_data(self, **kwargs):
		context = super(RemoteListView, self).get_context_data(**kwargs)

		developer = get_object_or_404(users.User, auth_user=self.request.user)

		context['remote_list'] = remotes.Remote.objects.filter(
			developer = developer
		)

		context['accesible_remote_list'] = remotes.Remote.objects.filter(
			users__id=developer.pk
		)

		return context

class CreateRemoteView(SupremoteLoginRequiredMixin, generic.CreateView):
	template_name = "core/remote_add.html"
	form_class = forms.RemoteCreateForm
	model = remotes.Remote
	success_url = reverse_lazy('core:remote_list')

	def get_initial(self):
		return {
			'developer': get_object_or_404(users.User, auth_user=self.request.user),
		}

	def form_valid(self, form):
		messages.success(self.request, "Remote created successfuly.")
		return super(CreateRemoteView, self).form_valid(form)

class EditRemoteView(SupremoteLoginRequiredMixin, generic.UpdateView):
	template_name = "core/remote_edit.html"
	form_class = forms.RemoteEditForm
	model = remotes.Remote
	success_url = reverse_lazy('core:remote_list')
	
	def get_object(self, queryset=None):
		remote_id = self.kwargs.pop('remote_id')
		remote_key = self.kwargs.pop('remote_key')

		return remotes.Remote.objects.get(
			pk=remote_id,
			key=remote_key
		)


	def form_valid(self, form):
		messages.success(self.request, "Remote edited successfuly.")
		return super(EditRemoteView, self).form_valid(form)


class DeleteUserRemoteView(SupremoteLoginRequiredMixin, generic.RedirectView):

	permanent = False

	def post(self, request, *args, **kwargs):

		self.user_id = request.POST['user_id']
		self.remote_id = request.POST['remote_id']

		remote = get_object_or_404(remotes.Remote, pk=self.remote_id)
		user = get_object_or_404(users.User, pk=self.user_id)

		remote.users.remove(user)
		remote.save()

		self.remote = remote

		messages.info(request, 'The User has been unassigned from the Remote')

		return redirect(self.get_redirect_url(*args, **kwargs))

	def get_redirect_url(self, *args, **kwargs):
		return reverse('core:remote_manage_users', kwargs={
			'remote_id': self.remote.pk,
			'remote_key': self.remote.key,
		})


class DeleteOriginView(SupremoteLoginRequiredMixin, generic.DeleteView):
	success_url = reverse_lazy('core:remote_manage_origins')

	def get_success_url(self):
		return reverse('core:remote_manage_origins', kwargs=self.kwargs)

	def post(self, request, *args, **kwargs):
		self.socket_origin = request.POST['origin_id']
		return super(DeleteOriginView, self).post(request, *args, **kwargs)

	def get_object(self, queryset=None):
		return remotes.SocketOrigin.objects.get(
			pk=self.socket_origin,
			remote__developer__auth_user=self.request.user,
		)

	def delete(self, request, *args, **kwargs):
		messages.success(request, "The origin has been deleted.")
		return super(DeleteOriginView, self).delete(request, *args, **kwargs)

class DeleteRemoteView(SupremoteLoginRequiredMixin, generic.DeleteView):
	success_url = reverse_lazy('core:remote_list')
	
	def post(self, request, *args, **kwargs):
		self.remote_id = request.POST['remote_id']
		return super(DeleteRemoteView, self).post(request, *args, **kwargs)

	def get_object(self, queryset=None):
		return remotes.Remote.objects.get(
			developer__auth_user=self.request.user,
			pk=self.remote_id
		)

	def delete(self, request, *args, **kwargs):
		messages.success(request, "The Remote has been deleted.")
		return super(DeleteRemoteView, self).delete(request, *args, **kwargs)


class LogoutView(SupremoteLoginRequiredMixin, generic.RedirectView):
	url = reverse_lazy('core:index')
	def get(self, request, *args, **kwargs):
		logout(request)
		return super(LogoutView, self).get(request, *args, **kwargs)

