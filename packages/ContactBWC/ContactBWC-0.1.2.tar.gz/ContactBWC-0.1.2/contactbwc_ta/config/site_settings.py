import logging
from os import path

from .settings import Default, app_package

class Dev(Default):
    def init(self):
        Default.init(self)
        myemail = 'rsyring@gmail.com'
        self.apply_dev_settings(myemail)

        self.add_component(app_package, 'templating', 'templatingbwc')
        self.template.default = 'templating:admin/layout.html'
        self.template.admin = 'templating:admin/layout.html'
        self.name = 'ContactBWC test'

        from blazeweb.logs import setup_stdout_logging
        setup_stdout_logging(logging.DEBUG, 'blazeweb.application')

        self.components.auth.admin.username = 'rsyring'
        self.components.auth.admin.password = 'pass'
        self.components.auth.admin.email = myemail

        self.db.url = 'sqlite:///%s' % path.join(self.dirs.data, 'test_application.db')
