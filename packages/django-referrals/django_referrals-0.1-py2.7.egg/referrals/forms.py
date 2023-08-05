from django import forms
from django.contrib.auth.models import User
 
class RegistrationForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField()
