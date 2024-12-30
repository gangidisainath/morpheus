from django.urls import path 
from . import views 

urlpatterns=[
    path('',views.home,name='home'),
    path('create',views.create_form,name='create'),
    path('user',views.user,name='user'),
    path('form/<int:form_id>',views.view_form,name='view_form'),
    path('manage',views.manage,name='manage'),
    path('editform',views.editform,name='editform'),
    path('edittemplate/<int:form_id>',views.edittemplate,name='edittemplate'),
    path('deletefields/<int:form_id>',views.deletefields,name='deletefields'),
    path('addfield/<int:form_id>',views.addfield,name='addfield'),
    path('viewresponse/<int:form_id>',views.viewresponse,name='viewresponse'),
    path('view_analytics/<int:form_id>',views.view_analytics,name='view_analytics'),

]
