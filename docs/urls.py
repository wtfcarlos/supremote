# -*- coding: utf8 -*-
from __future__ import unicode_literals
from django.conf.urls import patterns, include, url
from . import views 

urlpatterns = patterns('',
  url(r'^$', views.IndexView.as_view(), name="index"),
)