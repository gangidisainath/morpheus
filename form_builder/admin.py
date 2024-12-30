from django.contrib import admin
from .models import formfield, formtemplate,userresponse

@admin.register(formtemplate)
class FormAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(formfield)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('form', 'label', 'question_type')
@admin.register(userresponse)
class userresponseAdmin(admin.ModelAdmin):
    list_display = ('form', 'response')