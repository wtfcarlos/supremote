from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
	url(r'^auth/$', 'rest_framework.authtoken.views.obtain_auth_token'),
	url(r'^me/$', views.ProfileView.as_view(), name="me"),
	url(r'^remotes/(?P<remote_id>\d+)/$', views.RetrieveRemoteView.as_view(), name="remote_get"),
	url(r'^remotes/$', views.RemoteListView.as_view(), name="remote-list"),
	url(r'^remotes/save-values/$', views.RemoteValuesChangeView.as_view(), name="remote-save-values"),
	url(r'^remotes/trigger-action/$', views.RemoteTriggerActionView.as_view(), name="remote-save-values")
)