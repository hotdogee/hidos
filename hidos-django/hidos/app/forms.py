"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from allauth.account.forms import SignupForm

class LoginForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'mdl-textfield__input',
                                   }))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'mdl-textfield__input',
                                   }))
### overwrite allauth signupform (which is maybe not be a good way to do this)
class RegisterForm(SignupForm):
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'mdl-textfield__input'
                               }))
    email = forms.EmailField(widget=forms.TextInput({
                                    'class': 'mdl-textfield__input'
                                }))

    ### password should modify later
    password1 = forms.CharField(label=_("Password"),
                                widget=forms.PasswordInput({
                                    'class': 'mdl-textfield__input'
                                }))


    password2 = forms.CharField(label=_("Password"),
                            widget=forms.PasswordInput({
                                'class': 'mdl-textfield__input'
                            }))

