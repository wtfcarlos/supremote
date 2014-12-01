# -*- coding: utf8 -*-
from __future__ import unicode_literals
from django.views import generic
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, get_object_or_404
from django.template import RequestContext

from braces.views import LoginRequiredMixin

from users import models as users
from fields import models as fields
from remotes import models as remotes

from . import forms



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
					redirect_url = reverse('core:remote_list')
				else:
					redirect_url = reverse('core:index')
			else:
				redirect_url = None

		return redirect(redirect_url, context_instance=RequestContext(request))


class RemoteListView(LoginRequiredMixin, generic.ListView):
	template_name = "core/remote_list.html"
	model = remotes.Remote

	def get_queryset(self):
		# TODO - Separate LoginRequired for Developers and End Users
		developer = get_object_or_404(users.Developer, auth_user=self.request.user)
		return remotes.Remote.objects.filter(
			developer = developer
		)

class CreateRemoteView(LoginRequiredMixin, generic.FormView):
	template_name = "core/remote_add.html"
	form_class = forms.RemoteCreateForm
	success_url = reverse_lazy('core:remote_list')

	def get_initial(self):
		return {
			'developer': get_object_or_404(users.Developer, auth_user=self.request.user),
		}

	def form_valid(self, form):
		form.save()
		messages.success(self.request, "Remote created successfuly.")
		return super(CreateRemoteView, self).form_valid(form)

class LogoutView(LoginRequiredMixin, generic.RedirectView):
	url = reverse_lazy('core:index')
	def get(self, request, *args, **kwargs):
		logout(request)
		return super(LogoutView, self).get(request, *args, **kwargs)

