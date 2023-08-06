from distutils.core import setup
from openonmobile import __version__, __author__, __email__


long_description = open('README.rst').read()


setup(
    name='django-openonmobile',
    version=__version__,
    url='http://bitbucket.org/ferranp/django-openonmobile',
    author=__author__,
    author_email=__email__,
    license='GPL',
    packages=['openonmobile', 'openonmobile.templatetags'],
    package_data={'openonmobile': ['fixtures/*.json']},
    data_files=[('', ['README.rst'])],
    description='Open current URL on a mobile with a QR code',
    long_description=long_description,
    install_requires=["PIL==1.1.7", "qrcode==2.4.1"],
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Topic :: Internet :: WWW/HTTP :: Dynamic Content']
)
