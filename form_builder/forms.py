from django import forms
from django.forms import modelformset_factory
from .models import formfield,formtemplate,userresponse

class FormCreateForm(forms.ModelForm):
    class Meta:
        model =formtemplate
        fields = ['name','description']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = formfield
        fields = ['label', 'question_type', 'options', 'order']

        
QuestionFormSet = modelformset_factory(formfield,form=QuestionForm,extra=100
)