# -*- coding: utf-8 -*-
from blazeweb.routing import url_for
from blazeweb.utils import redirect
from blazeweb.views import View

from compstack.common.lib.views import FormMixin, CrudBase
from compstack.contact.forms import MakeContactForm, ContactForm
from compstack.contact.helpers import send_contact_email
from compstack.contact.model.entities import Contact
from compstack.datagrid.lib import DataGrid, Col, YesNo, Link
from compstack.sqlalchemy import db

class MakeContact(View, FormMixin):
    def setup_view(self, slug=None):
        self.slug = slug
        self.form_init(MakeContactForm)

    def form_assign_defaults(self):
        if self.slug:
            self.form.els.contact_to.defaultval = self.slug

    def form_on_valid(self):
        els = self.form.els

        try:
            contact_to = Contact.get_by(name_url_slug=els.contact_to.value).email
        except AttributeError as e:
            if 'contact_to' not in str(e):
                raise
            contact_to = None

        send_contact_email(
            contact_to,
            els.from_name.value,
            els.email.value,
            els.phone.value,
            els.subject.value,
            els.body.value,
            []
        )

        redirect(url_for('contact:thank_you.html'))

class ContactCRUD(CrudBase):
    def init(self):
        CrudBase.init(self, 'Contact', 'Contacts', ContactForm, Contact)
        self.require_all = 'contact-manage'

    def manage_init_grid(self):
        dg = DataGrid(
            db.sess.execute,
            per_page=30,
            class_='datagrid'
            )
        dg.add_col(
            'id',
            Contact.id,
            inresult=True
        )
        dg.add_tablecol(
            Col('Actions',
                extractor=self.manage_action_links,
                width_th='8%'
            ),
            Contact.id,
            sort=None
        )
        dg.add_tablecol(
            Col('Name'),
            Contact.name,
            filter_on=True,
            sort='both'
        )
        dg.add_tablecol(
            Col('Email'),
            Contact.email,
            filter_on=True,
            sort='both'
        )
        dg.add_tablecol(
            Col('URL'),
            Contact.name_url_slug,
            filter_on=True,
            sort='both'
        )
        return dg

