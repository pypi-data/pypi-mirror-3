import sys, os
from setuptools import setup, find_packages
from setuptools.command.develop import develop as STDevelopCmd

from contactbwc import VERSION

cdir = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(cdir, 'readme.rst')).read()
CHANGELOG = open(os.path.join(cdir, 'changelog.rst')).read()

class DevelopCmd(STDevelopCmd):
    def run(self):
        # testing requirements
        self.distribution.install_requires.append('pyquery')
        STDevelopCmd.run(self)

setup(
    name='ContactBWC',
    version=VERSION,
    description="contact component for the BlazeWeb framework",
    long_description=README + '\n\n' + CHANGELOG,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
    ],
    author='Randy Syring',
    author_email='rsyring@gmail.com',
    url='https://bitbucket.org/rsyring/contactbwc',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'AuthBWC',
        # required for control panel code, annoying!
        'BaseBWA'
    ],
    cmdclass = {
        'develop': DevelopCmd
    },
)
