from django import forms
from webshop.models import Salutation, City


class RegistrationForm(forms.Form):
    email = forms.EmailField()
    salutation = forms.ModelChoiceField(queryset=Salutation.objects.all())
    first_name = forms.CharField()
    last_name = forms.CharField()
    street_name = forms.CharField()
    street_number = forms.CharField()
    zip_code = forms.IntegerField(min_value=1000, max_value=9999)
    city = forms.CharField()

    def clean_city(self):
        # Check that the two password entries match
        city = self.cleaned_data['city']
        zip_code = self.cleaned_data['zip_code']
        try:
            City.objects.get(name=city, zip_code=zip_code)
        except City.DoesNotExist:
            raise forms.ValidationError(
                "The zip code and the city don't match.")
        return city
