from mailer import send_mail
from cccontact import settings as c_settings

def send_contact_form_email(sender, request, form, **kwargs):
    """sends the email from the contact form"""
    data = form.cleaned_data
    # TODO : handle the fail from newlines in the headers
    send_mail(
            #
            # TODO: make a more intelligent body! and combine
            # the subject with the name and phone number of the 
            # person
            data['subject'],
            data['m'],
            data['email'],
            c_settings.RECIPIENTS)
