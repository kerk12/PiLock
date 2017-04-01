from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(max_length=10, label="Username")
    password = forms.PasswordInput()

