from django import forms
from django.forms import Textarea
from blog.models import *

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        
        
class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    message = forms.CharField(max_length=800)
    email = forms.EmailField()
    