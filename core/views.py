# -*- coding: utf8 -*-
from __future__ import unicode_literals
from django.views import generic
from django.core.urlresolvers import reverse_lazy, reverse
from django.core.mail import send_mail, EmailMessage
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, get_object_or_404
from django.template import RequestContext

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

		context['signup_form'] = UserCreationForm()
		context['login_form'] = AuthenticationForm(self.request, self.request.POST or None)

		return context

	def post(self, request, *args, **kwargs):
		context = self.get_context_data(**kwargs)
		redirect_url = None

		if 'action' in request.POST:
			if request.POST['action'] == 'login':
				login_form = context['login_form']
				if login_form.is_valid():



					user = login_form.get_user()
					login(self.request, user)
					if 'next' in self.request.GET:
						redirect_url = self.request.GET['next']
					else:
						redirect_url = reverse('core:remote_list')
				else:
					redirect_url = reverse('core:index')
			else:
				redirect_url = None

		return redirect(redirect_url, context_instance=RequestContext(request))


class InvitationAcceptView(SupremoteLoginRequiredMixin, generic.TemplateView):
	template_name = "core/base.html"


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
		messages.success(self.request, 'The invitation has been sent.')

		email = form.cleaned_data['email']

		message = EmailMessage(subject="Supremote Invitation", from_email="noreply@supremote.com", to=[email,], body="Hiieee")

		invitation = invitations.Invitation(to=email)
		invitation.save()

		message.send()
		

		return super(ManageUsersRemoteView, self).form_valid(form)

	def get_success_url(self):
		return reverse_lazy('core:remote_manage_users', kwargs=self.kwargs)






class RemoteListView(SupremoteLoginRequiredMixin, generic.ListView):
	template_name = "core/remote_list.html"
	model = remotes.Remote

	def get_queryset(self):
		# TODO - Separate LoginRequired for Developers and End Users
		developer = get_object_or_404(users.User, auth_user=self.request.user)
		relevant_remotes = remotes.Remote.objects.filter(
			developer = developer
		)
		return relevant_remotes

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

