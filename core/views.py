# -*- coding: utf8 -*-
from __future__ import unicode_literals
from django.views import generic
from django.core.urlresolvers import reverse_lazy, reverse
from django.core.mail import send_mail, EmailMessage
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseForbidden
from braces.views import LoginRequiredMixin


from users import models as users
from fields import models as fields
from remotes import models as remotes
from invitations import models as invitations

from . import forms


class SupremoteLoginRequiredMixin(LoginRequiredMixin):
	login_url = reverse_lazy("core:index")


class IndexView(generic.TemplateView):

	template_name = "core/index.html"

	def get(self, request, *args, **kwargs):
		if request.user.is_authenticated():
			return redirect(reverse('core:remote_list'))
		return super(IndexView, self).get(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(IndexView, self).get_context_data(**kwargs)

		context['signup_form'] = forms.SignupForm(data=self.request.POST or None)
		context['login_form'] = AuthenticationForm(self.request, self.request.POST or None)

		return context

	def post(self, request, *args, **kwargs):
		context = self.get_context_data(**kwargs)
		redirect_url = None

		if 'action' in request.POST:
			user = None

			if request.POST['action'] == 'login':
				login_form = context['login_form']

				if login_form.is_valid():
					user = login_form.get_user()

			elif request.POST['action'] == 'sign-up':
				signup_form = context['signup_form']

				if signup_form.is_valid():
					signup_password = signup_form.cleaned_data['password1']
					user = signup_form.save()
					user = authenticate(username=user.username, password=signup_password)
					app_user = users.User(auth_user=user)
					app_user.save()
					

			if user is not None:
				login(self.request, user)
				if 'next' in self.request.GET:
					redirect_url = self.request.GET['next']
				else:
					redirect_url = reverse('core:remote_list')
			else:
				redirect_url = reverse('core:index')

		return redirect(redirect_url, context_instance=RequestContext(request))


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

