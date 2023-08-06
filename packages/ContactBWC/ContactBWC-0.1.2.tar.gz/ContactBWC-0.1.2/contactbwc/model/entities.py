from blazeutils.strings import simplify_string, randchars
from savalidation import validators as val
import sqlalchemy as sa
from sqlalchemy.orm import validates

from compstack.sqlalchemy import db
from compstack.sqlalchemy.lib.declarative import declarative_base, DefaultMixin
from compstack.sqlalchemy.lib.decorators import transaction
from compstack.sqlalchemy.lib.validators import validates_unique

Base = declarative_base()

__all__ = ['Contact']

class Contact(Base, DefaultMixin):
    __tablename__ = 'contact_contacts'

    name = sa.Column(sa.Unicode(255), nullable=False, unique=True)
    name_url_slug = sa.Column(sa.Unicode(255), nullable=False, unique=True)
    email = sa.Column(sa.Unicode(255), nullable=False)

    val.validates_constraints()
    val.validates_email('email')
    validates_unique('name','name_url_slug')

    @classmethod
    def _calc_nus(cls, name):
        nus = simplify_string(name)
        while nus and True:
            if not Contact.get_by(name_url_slug=nus):
                break
            nus = nus + randchars(2)
        return nus

    @validates('name')
    def _nus_validator(self, key, value):
        self.name_url_slug = self._calc_nus(value)
        return value

    def __repr__(self):
        return '<Contact "%s" : %s>' % (self.name, self.email)
