from django import forms
from webshop.models import (
                        Salutation,
                        City,
                        Picture,
                        Option,
                        CartPosition
                        )


class RegistrationForm(forms.Form):
    email = forms.EmailField()
    salutation = forms.ModelChoiceField(queryset=Salutation.objects.all())
    first_name = forms.CharField()
    last_name = forms.CharField()
    street_name = forms.CharField()
    street_number = forms.CharField(max_length=4)
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


class PictureForm(forms.ModelForm):
    def max_pictures(self):
        try:
            option = Option.objects.get(name='max_pictures')
            if option.enabled:
                return option.value
            else:
                return False
        except:
            return False

    def count_pictures(self, _article):
        count = Picture.objects.filter(article=_article.id).count()
        return count

    def clean(self):
        article = self.cleaned_data.get('article')
        print(self.max_pictures())
        if self.max_pictures():
            if (self.count_pictures(article) >= self.max_pictures()):
                raise forms.ValidationError("Only " + str(self.max_pictures())
                                            + " pictures per article allowed.")
        return self.cleaned_data

    class Meta:
        model = Picture
        fields = ['name', 'article', 'image']


class AddToCartForm(forms.Form):
    amount = forms.IntegerField(
        label='Amount in piece.',
        help_text="Enter a Value between 1 and 99.",
        initial=1)


class CartForm(forms.Form):
    amount_form = forms.FloatField(
                        label='pce',
                        )


class CheckoutForm(forms.Form):

    checkout = forms.BooleanField(
        required=True,
        label='Yes. I have read the General Terms and Conditions.')
