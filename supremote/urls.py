from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'supremote.views.home', name='home'),
    # url(r'^supremote/', include('supremote.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('api.urls')),
    url(r'^', include('core.urls', namespace="core")),
)

if settings.DEBUG:
	urlpatterns += patterns('',
   		 (r'^media/(?P<path>.*)$',
   		 'django.views.static.serve',
   		 {'document_root': settings.MEDIA_ROOT}),
	)
