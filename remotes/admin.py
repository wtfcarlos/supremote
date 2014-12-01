# -*- coding: utf8 -*-
from django.contrib import admin
from . import models

class RemoteAdmin(admin.ModelAdmin):
	model = models.Remote

admin.site.register(models.Remote, RemoteAdmin)