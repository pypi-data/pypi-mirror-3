from blazeweb.globals import settings
from formencode.validators import MaxLength

from compstack.common.lib.forms import Form
from compstack.contact.model.entities import Contact

class ContactForm(Form):
    def init(self):

        el = self.add_text('name', 'Name', required=True)
        el = self.add_text('email', 'Email', required=True)

        self.add_submit('submit')

class MakeContactForm(Form):
    def init(self):
        contacts = Contact.pairs('name_url_slug:name', order_by='name')

        if len(contacts) == 1:
            el = self.add_passthru('contact_to', contacts[0][0])
        elif len(contacts) > 1:
            el = self.add_select('contact_to', contacts, "Who to Contact", required=True)

        el = self.add_text('from_name', 'Your Name', required=True)
        el.add_processor(MaxLength(100))

        el = self.add_email('email', 'Your Email', required=True)
        el.add_processor(MaxLength(100))

        #if settings.modules.contactform.include_phone_field:
        #    el = self.add_text('phone', 'Your Phone', required=True)
        #    el.add_processor(MaxLength(15))
        el = self.add_passthru('phone', '')

        self.add_header('message-header', 'Your Message')

        el = self.add_text('subject', 'Subject', required=True)
        el.add_processor(MaxLength(100))

        el = self.add_textarea('body', 'Body', required=True)
        el.add_processor(MaxLength(500))

        #if settings.modules.contactform.allow_file_uploads:
        #    self.add_fixed('attachment_link', defaultval=link_to('Add Attachment', 'javascript:;'))
        #    self.add_file('attachment', '')

        self.add_submit('submit')
