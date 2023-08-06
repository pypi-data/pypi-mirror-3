from mailer import send_mail
from django.template import loader, Context
from cccontact import settings as c_settings

def send_contact_form_email(sender, request, form, **kwargs):
    """sends the email from the contact form"""
    data = form.cleaned_data
    # render the template
    t = loader.get_template('cccontact/message.txt')
    c = Context({
        'message': data.get('m'),
        'phone': data.get('phone')})
    message = t.render(c)
    # TODO : handle the fail from newlines in the headers
    send_mail(
            data['subject'],
            message,
            data['email'],
            c_settings.RECIPIENTS)
