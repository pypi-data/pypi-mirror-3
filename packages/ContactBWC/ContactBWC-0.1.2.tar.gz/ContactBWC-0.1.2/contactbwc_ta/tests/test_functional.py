from blazeweb.globals import ag, settings
from blazeweb.testing import TestApp, mockmail
from nose.plugins.skip import SkipTest
from nose.tools import eq_

from compstack.auth.lib.testing import login_client_with_permissions
from compstack.contact.model.entities import Contact

class TestMakeContact(object):

    @classmethod
    def setup_class(cls):
        cls.ta = TestApp(ag.wsgi_test_app)

    def setUp(self):
        Contact.delete_all()

    def test_makecontact(self):
        c = Contact.add(name=u"Foo Bar", email=u"foo@bar.com")
        c2 = Contact.add(name=u"Extra Bar", email=u"extra@bar.com")
        r = self.ta.get('/contact')
        d = r.pyq
        # heading
        eq_(d('h1').text(), 'Contact Us')

        # contact fields
        eq_(d('#make-contact-form-contact_to-row label').text(), 'Who to Contact:')
        eq_(d('#make-contact-form-from_name-row label').text(), 'Your Name:')
        eq_(d('#make-contact-form-email-row label').text(), 'Your Email:')

        # message
        eq_(d('h3').text(), 'Your Message')
        eq_(d('textarea#make-contact-form-body').text(), '')

    def test_makecontact_one_contact(self):
        c = Contact.add(name=u"Foo Bar", email=u"foo@bar.com")
        r = self.ta.get('/contact')
        d = r.pyq
        # heading
        eq_(d('h1').text(), 'Contact Us')

        # contact fields
        eq_(d('#make-contact-form-from_name-row label').text(), 'Your Name:')
        eq_(d('#make-contact-form-email-row label').text(), 'Your Email:')

        # message
        eq_(d('h3').text(), 'Your Message')
        eq_(d('textarea#make-contact-form-body').text(), '')

    def test_makecontact_default(self):
        r = self.ta.get('/contact')
        d = r.pyq
        # heading
        eq_(d('h1').text(), 'Contact Us')

        # contact fields
        eq_(d('#make-contact-form-contact_to-row label').text(), None)
        eq_(d('#make-contact-form-from_name-row label').text(), 'Your Name:')
        eq_(d('#make-contact-form-email-row label').text(), 'Your Email:')

        # message
        eq_(d('h3').text(), 'Your Message')
        eq_(d('textarea#make-contact-form-body').text(), '')

    def test_makecontact_slug(self):
        c = Contact.add(name=u"Foo2 Bar", email=u"foo2@bar.com")
        c2 = Contact.add(name=u"Extra2 Bar", email=u"extra2@bar.com")
        r = self.ta.get('/contact/foo2-bar')
        d = r.pyq
        # heading
        eq_(d('h1').text(), 'Contact Us')

        # contact fields
        eq_(d('#make-contact-form-contact_to-row label').text(), 'Who to Contact:')
        eq_(d('#make-contact-form-from_name-row label').text(), 'Your Name:')
        eq_(d('#make-contact-form-email-row label').text(), 'Your Email:')

        #check to make sure default value is set
        eq_(d('#make-contact-form-contact_to-row #make-contact-form-contact_to option:selected').text(), 'Foo2 Bar')

        # message
        eq_(d('h3').text(), 'Your Message')
        eq_(d('textarea#make-contact-form-body').text(), '')

    def make_post(self, to=None):
        topost = {
            'make-contact-form-submit-flag': '1',
            'from_name': 'fred',
            'email': 'fred@example.com',
            'subject': 'hi',
            'body': 'please call',
        }

        if to is not None:
            topost['contact_to'] = to
        return self.ta.post('/contact', topost, status=302)

    @mockmail
    def test_makecontact_post(self, mm_tracker=None):
        c = Contact.add(name=u'Foo Bar', email=u'foo@bar.com')
        r = self.make_post(c.name_url_slug)
        r = r.follow()
        assert 'Your message has been sent.  Thank you!' in r

        # check the email
        look_for=r"""
Called blazeweb.mail.EmailMessage(
    '[subprefix] Contact Form Submission',
    u'This message was submitted from the following contact form:.../contact\n\nFrom: fred\nEmail: fred@example.com\n\nSubject: hi\nMessage:\nplease call',
    None,
    [u'foo@bar.com'],
    reply_to=u'fred@example.com')
Called blazeweb.mail.EmailMessage.send()
""".strip()
        assert mm_tracker.check(look_for), mm_tracker.diff(look_for)

    @mockmail
    def test_makecontact_component_default(self, mm_tracker=None):
        # test that the default_to setting for this component has the desired
        # effect
        try:
            Contact.delete_all()
            settings.components.contact.default_to = u'testing_comp@default.com'
            r = self.make_post()

            # check the email
            look_for=r"""
Called blazeweb.mail.EmailMessage(
    '[subprefix] Contact Form Submission',
    u'This message was submitted from the following contact form:.../contact\n\nFrom: fred\nEmail: fred@example.com\n\nSubject: hi\nMessage:\nplease call',
    None,
    [u'testing_comp@default.com'],
    reply_to=u'fred@example.com')
Called blazeweb.mail.EmailMessage.send()
""".strip()
            assert mm_tracker.check(look_for), mm_tracker.diff(look_for)
        finally:
            # put it back
            settings.components.contact.default_to = None

    @mockmail
    def test_makecontact_admins_default(self, mm_tracker=None):
        # test that the admins setting for this component has the desired
        # effect
        try:
            settings.emails.admins = u'testing_admin@default.com'
            r = self.make_post()

            # check the email
            look_for=r"""
Called blazeweb.mail.EmailMessage(
    '[subprefix] Contact Form Submission',
    u'This message was submitted from the following contact form:.../contact\n\nFrom: fred\nEmail: fred@example.com\n\nSubject: hi\nMessage:\nplease call',
    None,
    [u'testing_admin@default.com'],
    reply_to=u'fred@example.com')
Called blazeweb.mail.EmailMessage.send()
""".strip()
            assert mm_tracker.check(look_for), mm_tracker.diff(look_for)
        finally:
            # put it back
            settings.emails.admins = None

class TestContactCRUD(object):

    @classmethod
    def setup_class(cls):
        cls.ta = TestApp(ag.wsgi_test_app)
        cls.ata = TestApp(ag.wsgi_test_app)
        perms = [u'contact-manage']
        cls.userid = login_client_with_permissions(cls.ata, perms)

    def setUp(self):
        Contact.delete_all()

    def test_perms(self):
        r = self.ta.get('/contacts/manage', status=401)

    def test_manage(self):
        c = Contact.add(name=u'Foo Bar', email=u'foo@example.com')

        r = self.ata.get('/contacts/manage')
        d = r.pyq
        assert 'Manage Contacts' in d('h2').text()
        assert "Foo Bar" in r
        assert "foo@example.com" in r
        assert "foo-bar" in r

    def test_add(self):
        topost = {
            'contact-form-submit-flag': '1',
            'name': 'Test Person',
            'email': 'test_add@example.com',
        }
        url = '/contacts/add'
        self.ata.post(url, topost, status=302)

        cur_contact = Contact.get_by(name=u"Test Person")
        assert cur_contact.name == "Test Person"
        assert cur_contact.name_url_slug == "test-person"
        assert cur_contact.email == 'test_add@example.com'

    def test_edit(self):
        cur_contact = Contact.add(name=u'Test Person', email=u'test@example.com')
        ccid = cur_contact.id

        topost = {
            'contact-form-submit-flag': '1',
            'name': 'Test Person',
            'email': 'test2@example.com',
        }
        url = '/contacts/edit/%s' % str(cur_contact.id)
        self.ata.post(url, topost, status=302)

        cc = Contact.get(ccid)
        assert cc.email == 'test2@example.com'

    def test_delete(self):
        assert Contact.count() == 0
        cur_contact = Contact.add(name=u'Test Tester', email=u'test@example.com')

        id = cur_contact.id
        url = '/contacts/delete/%s' % str(id)
        self.ata.get(url)

        assert Contact.count() == 0
