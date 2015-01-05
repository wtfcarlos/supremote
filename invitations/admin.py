# -*- coding: utf8 -*-
from django.contrib import admin
from . import models

class InvitationAdmin(admin.ModelAdmin):
	pass

admin.site.register(models.Invitation, InvitationAdmin)