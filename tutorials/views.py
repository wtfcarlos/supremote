# -*- coding: utf8 -*-
from __future__ import unicode_literals
from django.views import generic

class IndexView(generic.TemplateView):
	template_name = "tutorials/index.html"

class TrafficLightTutorialPart1View(generic.TemplateView):
	template_name = "tutorials/traffic_light_pt1.html"

class TrafficLightTutorialPart2View(generic.TemplateView):
	template_name = "tutorials/traffic_light_pt2.html"