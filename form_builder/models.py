from django.db import models
class formtemplate(models.Model):
    name=models.CharField(max_length=250)
    description=models.TextField(blank=True)
    count=models.IntegerField(default=0)
    def __str__(self):
        return self.name
class formfield(models.Model):
    field_types=[
        ('text','Text'),
        ('email','Email'),
        ('checkbox','Checkbox'),
        ('textarea','Text Area'),
        ('dropdown','drop-down'),
        ('number','number'),
    ]

    form=models.ForeignKey(formtemplate,related_name='questions',on_delete=models.CASCADE)
    label=models.CharField(max_length=250,unique=True)
    question_type=models.CharField(max_length=20,choices=field_types)
    options=models.TextField(blank=True,null=True,help_text="comma-separated options")
    order=models.PositiveIntegerField()

    
    def __str__(self):
        return self.label
class userresponse(models.Model):
    form=models.ForeignKey(formtemplate,related_name='responses',on_delete=models.SET_NULL,null=True)
    response=models.JSONField()
