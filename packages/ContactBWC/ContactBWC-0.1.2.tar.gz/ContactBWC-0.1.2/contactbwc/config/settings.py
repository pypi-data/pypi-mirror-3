# -*- coding: utf-8 -*-

from basebwa.lib.cpanel import ControlPanelSection, ControlPanelGroup, ControlPanelLink
from blazeweb.config import ComponentSettings

class Settings(ComponentSettings):
    def init(self):
        self.init_routing()

        ## Control Panel Links
        self.for_me.cp_nav.enabled = True
        self.for_me.cp_nav.section = ControlPanelSection(
            "Contact Form",
            'contact-manage',
            ControlPanelGroup(
                ControlPanelLink('Contact Add', 'contact:ContactCRUD', action='add'),
                ControlPanelLink('Contact Manage', 'contact:ContactCRUD', action='manage'),
            )
        )

        self.for_me.include_phone_field = False
        # set this to an email address or list of email addresses in order to
        # have the contact form email send to those addresses.  But, this ONLY
        # works when no contacts are setup in the DB for this module.
        self.for_me.default_to = None
        #self.for_me.allow_file_uploads = False

    def init_routing(self):
        self.add_route('/contact', endpoint='contact:MakeContact')
        self.add_route('/contact/<slug>', endpoint='contact:MakeContact')
        self.add_route('/contact/thank-you', endpoint='contact:thank_you.html')
        self.add_route('/contacts/<action>', endpoint='contact:ContactCRUD')
        self.add_route('/contacts/<action>/<int:objid>', endpoint='contact:ContactCRUD')
