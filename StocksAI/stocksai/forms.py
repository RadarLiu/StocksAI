from django import forms
import re

class AddCompanyForm(forms.Form):
  code = forms.CharField(label='Company Code', max_length=7)

  def clean(self):
    cleaned_data = super(AddCompanyForm, self).clean()
    code = cleaned_data.get("code")
    if re.search("^[A-Za-z]+$", code) is None:
      raise forms.ValidationError("Invalid code, must be a string of letters.")


class DelCompanyForm(forms.Form):
  code = forms.CharField(label='Company Code', max_length=7)

  def clean(self):
    cleaned_data = super(DelCompanyForm, self).clean()
