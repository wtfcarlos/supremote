# -*- coding: utf8 -*-
from django.contrib import admin
from . import models

class RemoteAdmin(admin.ModelAdmin):
	model = models.Remote

class SocketOriginAdmin(admin.ModelAdmin):
	model = models.SocketOrigin
	list_display = ['domain', 'remote']

class ActionThrottleAdmin(admin.ModelAdmin):
	model = models.ActionThrottle
	list_display = ['remote', 'key', 'status_code', 'created']

admin.site.register(models.Remote, RemoteAdmin)
admin.site.register(models.ActionThrottle, ActionThrottleAdmin)
admin.site.register(models.SocketOrigin, SocketOriginAdmin)