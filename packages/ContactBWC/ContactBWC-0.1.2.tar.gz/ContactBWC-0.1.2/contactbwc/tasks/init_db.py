from blazeweb.tasks import attributes

from compstack.auth.model.orm import Permission

@attributes('base-data')
def action_30_base_data():
    Permission.add_iu(name=u'contact-manage')
