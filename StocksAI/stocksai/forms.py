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


class EditUserInfoForm(forms.Form):
  email = forms.CharField(max_length=50, required=True,
    validators=[RegexValidator(r"^.*@.*$",message="Email format error")])
  first_name = forms.CharField(max_length=30, label="First Name",
    validators=[RegexValidator(r"^[a-zA-Z]*$", message="Enter only letters")])
  last_name = forms.CharField(max_length=30, label="Last Name",
    validators=[RegexValidator(r"^[a-zA-Z]*$", message="Enter only letters")])
  old_password = forms.CharField(max_length=20, label="Old Password", widget=forms.PasswordInput())
  password = forms.CharField(max_length=20, label="Password", widget=forms.PasswordInput(), required=False)
  password_repeat = forms.CharField(max_length=20, label="Confirm password", widget=forms.PasswordInput(), required=False)

  # Do not do cross-field validation here! (Do it in views.py)
  # Do not modify this method!
  def clean(self):
    cleaned_data = super(EditUserInfoForm, self).clean()
    return cleaned_data

  def clean_password(self):
    cleaned_data = super(EditUserInfoForm, self).clean()
    password = cleaned_data.get("password")
    if len(password) < 4 and len(password) > 0:
      raise forms.ValidationError("Password too short!")
    return password    


class RegistrationForm(forms.Form):
  username = forms.CharField(max_length=40, required=True,
    validators=[RegexValidator(r"^[0-9a-zA-Z]*$",message="Enter only letters and numbers")])
  email = forms.CharField(max_length=50, required=True,
    validators=[RegexValidator(r"^.*@.*$",message="Email format error")])
  first_name = forms.CharField(max_length=30, label="First Name",
    validators=[RegexValidator(r"^[a-zA-Z]*$", message="Enter only letters")])
  last_name = forms.CharField(max_length=30, label="Last Name",
    validators=[RegexValidator(r"^[a-zA-Z]*$", message="Enter only letters")])
  password = forms.CharField(max_length=20, label="Password", widget=forms.PasswordInput())
  password_repeat = forms.CharField(max_length=20, label="Confirm password", widget=forms.PasswordInput())

  # Do not do cross-field validation here! (Do it in views.py)
  # Do not modify this method!
  def clean(self):
    cleaned_data = super(RegistrationForm, self).clean()
    return cleaned_data

  # Do per-field validation in their respective method!
  def clean_username(self):
    cleaned_data = super(RegistrationForm, self).clean()
    username = cleaned_data.get("username")
    if User.objects.filter(username=username):
      raise forms.ValidationError("Username already exists!")
    return username

  def clean_password(self):
    cleaned_data = super(RegistrationForm, self).clean()
    password = cleaned_data.get("password")
    if len(password) < 4:
      raise forms.ValidationError("Password too short!")
    return password
