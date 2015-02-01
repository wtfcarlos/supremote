# -*- coding: utf8 -*-
from __future__ import unicode_literals
from django.conf.urls import patterns, include, url
from . import views 

urlpatterns = patterns('',
  url(r'^$', views.IndexView.as_view(), name="index"),

  url(r'^terms/$', views.TermsAndConditionsView.as_view(), name="terms"),
  url(r'^privacy/$', views.PrivacyView.as_view(), name="privacy"),

  url(r'^actions/$', views.TestActionReceiveView, name="actions"),
  url(r'^endpoint_process/$', views.TestEndpointProcessView, name="test_endpoint"),

  url(r'^signup/$', views.SignupView.as_view(), name="signup"),
  url(r'^remotes/$', views.RemoteListView.as_view(), name="remote_list"),
  url(r'^account/$', views.AccountSettingsView.as_view(), name="account_settings"),
  url(r'^remote/create/$', views.CreateRemoteView.as_view(), name="remote_create"),
  url(r'^remote/(?P<remote_id>\d+)/(?P<remote_key>[\w_-]+)/edit/$', views.EditRemoteView.as_view(), name="remote_edit"),

  url(r'^remote/(?P<remote_id>\d+)/(?P<remote_key>[\w_-]+)/users/$', views.ManageUsersRemoteView.as_view(), name="remote_manage_users"),

  url(r'^remote/(?P<remote_id>\d+)/(?P<remote_key>[\w_-]+)/origins/manage/$', views.ManageRemoteOriginsView.as_view(), name="remote_manage_origins"),

  url(r'^remote/(?P<remote_id>\d+)/(?P<remote_key>[\w_-]+)/origins/delete/$', views.DeleteOriginView.as_view(), name="remote_delete_origin"),

  url(r'^remote/(?P<remote_id>\d+)/(?P<remote_key>[\w_-]+)/$', views.RemoteDetailView.as_view(), name="remote_detail"),

  url(r'^remote/(?P<remote_id>\d+)/(?P<remote_key>[\w_-]+)/trigger_action/$', views.RemoteTriggerActionView.as_view(), name="remote_trigger_action"),
  
  url(r'^remote/delete/$', views.DeleteRemoteView.as_view(), name="remote_delete"),

  url(r'^invitation/(?P<nonce>[\w-]+)/$', views.InvitationAcceptView.as_view(), name="invitation_link"),

  url(r'^invitation/(?P<invitation_id>\d+)/resend/$', views.ResendInvitationView.as_view(), name="resend_invitation"),

  url(r'^remote/user/delete/$', views.DeleteUserRemoteView.as_view(), name="remove_remote_user"),

  url(r'^logout/$', views.LogoutView.as_view(), name="logout"),

)