from django import forms
from django.contrib.auth import authenticate
from django.utils.translation import gettext as _

class UsersLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget = forms.PasswordInput,)

    def __init__(self, *args, **kwargs):
        super(UsersLoginForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                "name":"username"})


    def clean(self, *args, **keyargs):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:
            user = authenticate(username = username, password = password)
            if not user:
                raise forms.ValidationError("Username or password incorrect")
            if not user.is_active:
                raise forms.ValidationError("User is no longer active")

        return super(UsersLoginForm, self).clean(*args, **keyargs)