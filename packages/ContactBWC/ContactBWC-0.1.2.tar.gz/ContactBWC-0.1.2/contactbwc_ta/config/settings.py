from os import path

from blazeweb.config import DefaultSettings

basedir = path.dirname(path.dirname(__file__))
app_package = path.basename(basedir)

class Default(DefaultSettings):
    def init(self):
        self.dirs.base = basedir
        self.app_package = app_package
        DefaultSettings.init(self)
        self.init_components()

    def init_components(self):
        self.add_component(app_package, 'sqlalchemy', 'sqlalchemybwc')
        self.add_component(app_package, 'common', 'commonbwc')
        self.add_component(app_package, 'contact', 'contactbwc')
        self.add_component(app_package, 'datagrid', 'datagridbwc')
        self.add_component(app_package, 'auth', 'authbwc')
        self.add_component(app_package, 'templating', 'templatingbwc')

class Test(Default):
    def init(self):
        Default.init(self)
        self.apply_test_settings()

        self.emails.admins = 'admin@example.com'
        self.emails.from_default = 'from@example.com'
        self.email.subject_prefix = '[subprefix] '

        self.template.default = 'common:layout_testing.html'
        self.template.admin = 'common:layout_testing.html'

        self.db.url = 'sqlite://'

        # uncomment this if you want to use a database you can inspect
        #from os import path
        #self.db.url = 'sqlite:///%s' % path.join(self.dirs.data, 'test_application.db')

        # we get errors in testing when this isn't set b/c there is no-where
        # to go after login
        self.add_route('/', 'contact:MakeContact')
try:
    from site_settings import *
except ImportError, e:
    if 'No module named site_settings' not in str(e):
        raise
