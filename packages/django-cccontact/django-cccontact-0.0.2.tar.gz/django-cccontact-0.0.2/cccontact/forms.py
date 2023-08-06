from django import forms


class ContactForm(forms.Form):
    name = forms.CharField()
    subject = forms.CharField()
    email = forms.EmailField()
    m = forms.CharField(
            widget=forms.Textarea(),
            label='Your Message')
    phone = forms.CharField(
            required=False)
    # this field is a honeypot trap
    message = forms.CharField(
            widget=forms.Textarea(),
            required=False)
