# -*- coding: utf8 -*-
from __future__ import unicode_literals
from django.conf.urls import patterns, include, url
from . import views 

urlpatterns = patterns('',
  url(r'^$', views.IndexView.as_view(), name="index"),
  url(r'^remotes/$', views.RemoteListView.as_view(), name="remote_list"),
  url(r'^remote/create/$', views.CreateRemoteView.as_view(), name="remote_create"),
  url(r'^logout/$', views.LogoutView.as_view(), name="logout"),

)