# -*- coding: utf8 -*-
from django.contrib import admin
from . import models

class DeveloperAdmin(admin.ModelAdmin):
	model = models.Developer

admin.site.register(models.Developer, DeveloperAdmin)