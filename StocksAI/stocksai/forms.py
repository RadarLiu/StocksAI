from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
import re

class AddCompanyForm(forms.Form):
  code = forms.CharField(label="Company Code", max_length=7)
  industry = forms.CharField(label="Company Code", max_length=100)

  def clean(self):
    cleaned_data = super(AddCompanyForm, self).clean()
    code = cleaned_data.get("code")
    if re.search("^[A-Za-z]+$", code) is None:
      raise forms.ValidationError("Invalid code, must be a string of letters.")


class DelCompanyForm(forms.Form):
  code = forms.CharField(label="Company Code", max_length=7)

  def clean(self):
    cleaned_data = super(DelCompanyForm, self).clean()


class RegistrationForm(forms.Form):
  username = forms.CharField(max_length=40, required=True,
    validators=[RegexValidator(r"^[0-9a-zA-Z]*$",message="Enter only letters and numbers")])
  email = forms.CharField(max_length=50, required=True)
  first_name = forms.CharField(max_length=30, label="First Name",
    validators=[RegexValidator(r"^[a-zA-Z]*$", message="Enter only letters")])
  last_name = forms.CharField(max_length=30, label="Last Name",
    validators=[RegexValidator(r"^[a-zA-Z]*$", message="Enter only letters")])
  password = forms.CharField(max_length=20, label="Password", widget=forms.PasswordInput())
  password_repeat = forms.CharField(max_length=20, label="Confirm password", widget=forms.PasswordInput())

  def clean(self):
    cleaned_data = super(RegistrationForm, self).clean()

    p1 = cleaned_data.get("password")
    p2 = cleaned_data.get("password_repeat")
    if p1 and p2 and p1 != p2:
      raise forms.ValidationError("Passwords did not match!")
    e = cleaned_data.get("email")
    if e and not "@" in e:
      raise forms.ValidationError("Email format error!")
    return cleaned_data

  def clean_username(self):
    username = self.cleaned_data.get("username")
    if User.objects.filter(username=username):
      raise forms.ValidationError("Username already exists!")
    return username
