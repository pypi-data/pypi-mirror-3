from model.orm import Email
from pysmvt import rg, db, settings, modimportauto
from pysmvt.utils import urlslug
modimportauto('contactform.utils', 'send_contact_email')

def send_contact_form(**kwargs):
    phone = kwargs['phone'] if settings.modules.contactform.include_phone_field else None
    attachments = rg.request.files.getlist('attachment') if settings.modules.contactform.allow_file_uploads else []
    send_contact_email(contact_get_email_by_url_slug(kwargs['to']), kwargs['from_name'], kwargs['email_address'], phone, kwargs['subject'], kwargs['message'], attachments)

def contact_add(safe=False, **kwargs):
    try:
        contact_update(None, **kwargs)
    except Exception, e:
        if safe == False or safe not in str(e):
            raise

def contact_update(id, **kwargs):
    dbsess = db.sess
    if id is not None:
        e = Email.get_by(id=id)
    else:
        e = Email()
    try:
        if not kwargs.get('name_url_slug'):
            kwargs['name_url_slug'] = urlslug(kwargs['name'])
        e.from_dict(kwargs)
        dbsess.commit()
    except:
        dbsess.rollback()
        raise

def contact_add(safe=False, **kwargs):
    """ safe allows us to use this function and not get exceptions thrown """
    try:
        contact_update(None, **kwargs)
    except Exception, e:
        if safe == False or safe not in str(e):
            raise

def contact_get(id):
    return Email.query.get(id)

def contact_get_by_name(name):
    return Email.get_by(name=name)
    
def contact_get_by_url_slug(name):
    return Email.get_by(name_url_slug=name)

def contact_get_email_by_url_slug(us):
    return Email.get_by(name_url_slug=us).email_address
    
def contact_list():
    return Email.query.order_by('name').all()

def contact_list_options():
    order_fields = 'sort_order, name' if settings.modules.contactform.allow_sort_order else 'name'
    return [(e.name_url_slug, e.name) for e in Email.query.order_by(order_fields)]

def contact_delete(id):
    e = Email.get_by(id=id)
    if e is not None:
        e.delete()
        try:
            db.sess.commit()
        except:
            db.sess.rollback()
            raise
        return True
    return False
