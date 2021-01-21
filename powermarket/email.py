from django.conf import settings
from django.core.mail import (
    get_connection,
    EmailMultiAlternatives,
)
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from smtplib import SMTPRecipientsRefused

def send_templated_email(
        subject,
        recipient_list=None,
        text_template=None,
        html_template=None,
        context=None,
        from_email=None,
        skip_sending=False,
        headers=None,
        cc=None,
        bcc=None,
        fail_silently=False,
):

    if not text_template:
        raise Exception(
            _("You need to specify a text_template")
        )
    if not recipient_list:
        raise Exception(
            _("You need to specify at least one recipient.")
        )

    if not from_email:
        from_email = settings.DEFAULT_FROM_EMAIL

    text_message = render_to_string(text_template, context)
    context['subject'] = subject

    if recipient_list:
        if type(recipient_list[0]) == tuple:
            recipient_list = [entry[1] for entry in recipient_list]

    email = EmailMultiAlternatives(
        subject,
        text_message,
        from_email,
        recipient_list,
        connection=get_connection(),
        headers=headers,
        cc=cc,
        bcc=bcc,
    )

    # Attach HTML message if template is given.
    if html_template:
        html_message = render_to_string(html_template, context)
        email.attach_alternative(html_message, 'text/html')

    if not skip_sending:
        success=False
        try:
            success=email.send(fail_silently=fail_silently)
        except SMTPRecipientsRefused:
            print("Invalid email address or some other issue prevented sending the report")
            success=False

        return success
    else:
        return False
