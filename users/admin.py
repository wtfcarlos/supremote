# -*- coding: utf8 -*-
from django.contrib import admin
from . import models

class UserAdmin(admin.ModelAdmin):
	model = models.User

admin.site.register(models.User, UserAdmin)