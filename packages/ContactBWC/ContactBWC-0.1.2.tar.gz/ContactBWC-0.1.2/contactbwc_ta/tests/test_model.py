from nose.plugins.skip import SkipTest
from nose.tools import eq_

from compstack.sqlalchemy import db
from compstack.sqlalchemy.lib.helpers import is_fk_exc, is_null_exc
from contactbwc.model.entities import Contact

class TestContact(object):

    def setUp(self):
        Contact.delete_all()

    def test_add(self):
        c = Contact.add(name=u'a b', email=u'a@example.com')
        assert c.id > 0
        assert c.createdts
        eq_(c.name_url_slug, 'a-b')

    def test_edit(self):
        # edit method
        c = Contact.add(name=u'a b', email=u'a@example.com')
        Contact.edit(c.id, name=u'b c')
        c = Contact.get(c.id)
        eq_(c.name_url_slug, 'b-c')

    def test_edit2(self):
        # edit by attribute
        c = Contact.add(name=u'a b', email=u'a@example.com')
        c.name=u'b c'
        db.sess.commit()
        eq_(c.name_url_slug, 'b-c')


    def test_delete(self):
        c = Contact.add(name=u'a b', email=u'a@example.com')
        assert Contact.get(c.id) is not None
        Contact.delete(c.id)
        assert Contact.get(c.id) is None

    def test_to_string(self):
        c = Contact.add(name=u'a b', email=u'a@example.com')
        eq_(str(c), '<Contact "a b" : a@example.com>')
