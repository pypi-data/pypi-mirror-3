from blazeutils.helpers import tolist
from blazeweb.content import getcontent
from blazeweb.globals import settings
import blazeweb.mail as bwm

def send_contact_email(to, from_name, email_address, phone, subject, body, attachments):
    subject_header = '%sContact Form Submission' % settings.email.subject_prefix
    mail_body = getcontent('contact:contact_email.txt', from_name=from_name, email_address=email_address, phone=phone, subject=subject, body=body)

    if to is None:
        to = settings.components.contact.default_to or settings.emails.admins

    email = bwm.EmailMessage(subject_header, mail_body.primary, None, tolist(to), reply_to=email_address)
    for att in attachments:
        if att.filename:
            email.attach(att.filename, att.stream.read(), att.content_type)
    email.send()
