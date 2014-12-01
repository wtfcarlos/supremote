# -*- coding: utf8 -*-
from django.contrib import admin
from . import models



class TextFieldAdmin(admin.ModelAdmin):
	model = models.TextField
	list_display = ['key', 'value']


class TextChoiceFieldAdmin(admin.TabularInline):
	model = models.TextChoice

class MultipleChoiceFieldAdmin(admin.ModelAdmin):
	model = models.MultipleChoiceField
	inlines = [TextChoiceFieldAdmin, ]
	list_display = ['key', 'value']

class BooleanFieldAdmin(admin.ModelAdmin):
	model = models.BooleanField
	list_display = ['key', 'value']

class NumberChoiceFieldAdmin(admin.ModelAdmin):
	model = models.NumberChoiceField
	list_display = ['key', 'value']

admin.site.register(models.TextField, TextFieldAdmin)
admin.site.register(models.MultipleChoiceField, MultipleChoiceFieldAdmin)
admin.site.register(models.BooleanField, BooleanFieldAdmin)
admin.site.register(models.NumberChoiceField, NumberChoiceFieldAdmin)




# class AbstractBaseField(TimeStampedModel):
# 	key = models.CharField(max_length=100)

# 	class Meta:
# 		abstract = True

# 	def __unicode__(self):
# 		return self.value

# class TextField(AbstractBaseField):
# 	value = models.CharField(max_length=140)

# class MultipleChoiceField(AbstractBaseField):
# 	value = models.ForeignKey("TextChoice")

# 	def __unicode__(self):
# 		return self.value.__unicode__()

# class TextChoice(models.Model):
# 	field = models.ForeignKey(MultipleChoiceField)
# 	value = models.CharField(max_length=50)

# 	def __unicode__(self):
# 		return self.value

# class BooleanField(AbstractBaseField):
# 	value = models.BooleanField()
# 	default = models.BooleanField(default=False)

# class NumberChoiceField(AbstractBaseField):
# 	lower = models.SmallIntegerField(default=1)
# 	upper = models.SmallIntegerField(default=10)
# 	value = models.SmallIntegerField(default=5)

