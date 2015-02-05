# -*- coding: utf8 -*-
from __future__ import unicode_literals
from django.views import generic

class IndexView(generic.TemplateView):
	template_name = "docs/index.html"