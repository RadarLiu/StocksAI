from django import forms

class AddCompanyForm(forms.Form):
  code = forms.CharField(label='Company Code', max_length=100)

  def clean(self):
      cleaned_data = super(AddCompanyForm, self).clean()
