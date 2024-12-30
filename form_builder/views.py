from django.shortcuts import render, redirect, get_object_or_404
from .models import formtemplate,formfield
from .forms import FormCreateForm, QuestionFormSet
from django.http import HttpResponse
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('agg')
import base64,io
from django.contrib.admin.views.decorators import staff_member_required
def home(request):
   form=formtemplate.objects.all()
   c=[]
   for i in form:
       c.append(len(i.responses.all()))
   form=zip(form,c)
   return render(request,'home.html',{'forms':form,'count':c})
@staff_member_required
def create_form(request):
    if request.method == 'POST':
        form = FormCreateForm(request.POST)
        question_formset = QuestionFormSet(request.POST)
        
        if form.is_valid() and question_formset.is_valid():
            new_form = form.save()

            questions = question_formset.save(commit=False)
            for question in questions:
                question.form = new_form
                question.save()

            return redirect('home')
        else:
            return HttpResponse('cannot have same labels')

    else:
        form = FormCreateForm()
        question_formset = QuestionFormSet(queryset=formfield.objects.none())

    return render(request, 'create_form.html', {
        'form': form,
        'question_formset': question_formset,
    })

@staff_member_required
def user(request):
    forms = formtemplate.objects.all()
    return render(request, 'user.html', {'forms': forms})
@staff_member_required
def manage(request):
   form=formtemplate.objects.all()
   return render(request,'manage.html',{'form':form})
@staff_member_required
def editform(request):
    form_id=request.POST.get('form_name')
    return render(request,'edittemplate.html',{'form_id':form_id})
def view_form(request, form_id):
    form = get_object_or_404(formtemplate, id=form_id)
    questions=form.questions.all().order_by('order')
    for i in questions:
     if i.options:
        i.options=list(map(str,i.options.split(',')))
        print(i.question_type,i.options)
    if request.method == 'POST':
        r={}
        for i in questions:
           if i.question_type=='checkbox':
             r[i.label]=request.POST.getlist('question_'+str(i.id)) 
           else:
               r[i.label]=request.POST.get('question_'+str(i.id))
        
        form.responses.create(response=r)
        form=formtemplate.objects.get(id=form_id)
        form.count+=1
        
        form.save()
        return redirect('home')
        
    
    return render(request, 'view_form.html', {'form': form,'questions':questions})
@staff_member_required
def edittemplate(request,form_id):
    template=formtemplate.objects.get(id=form_id)
    n=len(template.questions.all())
    if request.method == 'POST':
        
        question_formset = QuestionFormSet(request.POST)
        
        if question_formset.is_valid():
            questions = question_formset.save(commit=False)
            for question in questions[n:100]:
                question.form=template
                question.save()
           
            return redirect('home')

    else:
       
        question_formset = QuestionFormSet(queryset=formfield.objects.none())

    return render(request, 'new.html', {
        
        'question_formset': question_formset,
        'form':template.name
    })

def deletefields(request,form_id):
    template = formtemplate.objects.get(id=form_id)
    field=template.questions.all()
    if request.method=="POST":
        fields=request.POST.getlist('fields')
        for i in fields:
          for j in template.responses.all():
                 x=j 
                
                 del x.response[i]
                 x.save()
          template.questions.get(label=i).delete()
          template.save()
        
        if not field:
            formtemplate.objects.get(id=form_id).delete()
       
        return redirect('home')
    return render(request, 'deletefields.html', {'form': field,'name':template.name})
def addfield(request,form_id):
    if request.method == 'POST':
        question_formset = QuestionFormSet(request.POST)
        
        if question_formset.is_valid():
          
            template=formtemplate.objects.get(id=form_id)
            
            questions = question_formset.save(commit=False)
            for question in questions:
                question.form = template
                question.save()
                for i in template.responses.all():
                 x=i 
                 x.response[question.label]=None 
                 x.save()
                

            return redirect('home')

    else:
       
        question_formset = QuestionFormSet(queryset=formfield.objects.none())

    form=formtemplate.objects.get(id=form_id)
    return render(request,'addfield.html',{'question_formset':question_formset,'name':form.name})

def viewresponse(request,form_id):
    form=formtemplate.objects.get(id=form_id)
    question=form.questions.all()
    a= [i['response'] for i in form.responses.all().values()]

    return  render(request,'view responses.html',{'responses':a,'questions':question})

from collections import Counter

def view_analytics(request, form_id):
    img=[]
    form = formtemplate.objects.get(id=form_id)
    responses = form.responses.all()
    total_responses = responses.count()
    
    question_analytics = []
    fields=form.questions.all()
    
    for field in fields:
      if field.question_type in ['text','textarea','checkbox','dropdown']:
        answers = []
        for respons in responses:
            data = respons.response
            
            if field.label in data and data[field.label] is not None:
                answers.append(data[field.label]) 
                
        if field.question_type in ['text','textarea'] :
            words = [word.lower() for text in answers for word in text.split() if len(word) >= 5]
            
            word_counts = Counter(words)
            analytics = dict(word_counts.most_common(5))
            analytics['Others'] = sum(word_counts.values()) - sum(analytics.values())

        elif field.question_type == 'dropdown':
            option_counts = Counter(answers)
            analytics = dict(option_counts.most_common(5))
            analytics['Others'] = sum(option_counts.values()) - sum(analytics.values())

        elif field.question_type == 'checkbox':
            
            option_counts = Counter(tuple(answer) for answer in answers)
            
            analytics = dict(option_counts.most_common(5))
            
            analytics['Others'] = sum(option_counts.values()) - sum(analytics.values())

        question_analytics.append({
            'question': field.label,
            'analytics': analytics,
        })
        
        labels=[]
        data=[]
        for i,j in question_analytics[-1]['analytics'].items():
            labels.append(i)
            data.append(j)
        plt.figure(figsize=(2,2))
        plt.pie(data,labels=labels,autopct='%1.1f%%')
        plt.title('analytics')
    
        buffer=io.BytesIO()
        plt.savefig(buffer,format='png',bbox_inches='tight')
        buffer.seek(0)
        img.append(base64.b64encode(buffer.getvalue()).decode('utf-8'))
        plt.clf() 
        buffer.close()
          
    x=zip(question_analytics,img)
    return render(request, 'analytics.html', {
        'form': form,
        'total_responses': total_responses,
        'question_analytics': question_analytics,
        'img':img,
        'fields':fields,
        'x':x,
    })