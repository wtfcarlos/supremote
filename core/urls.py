# -*- coding: utf8 -*-
from __future__ import unicode_literals
from django.conf.urls import patterns, include, url
from . import views 

urlpatterns = patterns('',
  url(r'^$', views.IndexView.as_view(), name="index"),
  url(r'^remotes/$', views.RemoteListView.as_view(), name="remote_list"),
  url(r'^remote/create/$', views.CreateRemoteView.as_view(), name="remote_create"),
  url(r'^remote/(?P<remote_id>\d+)/(?P<remote_key>[\w_-]+)/edit/$', views.EditRemoteView.as_view(), name="remote_edit"),

  url(r'^remote/(?P<remote_id>\d+)/(?P<remote_key>[\w_-]+)/users/$', views.ManageUsersRemoteView.as_view(), name="remote_manage_users"),

  url(r'^remote/delete/$', views.DeleteRemoteView.as_view(), name="remote_delete"),

  url(r'^invitation/(?P<nonce>[\w-]+)/$', views.InvitationAcceptView.as_view(), name="invitation_link"),

  url(r'^invitation/(?P<invitation_id>\d+)/resend/$', views.ResendInvitationView.as_view(), name="resend_invitation"),

  url(r'^remote/user/delete/$', views.DeleteUserRemoteView.as_view(), name="remove_remote_user"),

  url(r'^logout/$', views.LogoutView.as_view(), name="logout"),

)