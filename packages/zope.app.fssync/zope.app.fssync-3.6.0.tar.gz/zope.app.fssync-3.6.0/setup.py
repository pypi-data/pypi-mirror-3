import os

from setuptools import setup, find_packages, Extension

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.app.fssync',
      version = '3.6.0',
      url = 'http://pypi.python.org/pypi/zope.app.fssync',
      license = 'ZPL 2.1',
      description = "Filesystem synchronization utility for Zope 3.",
      author= 'Zope Corporation and Contributors',
      author_email= 'zope3-dev@zope.org',
      long_description = (read('README.txt')
                          + '\n\n' +
                          read('CHANGES.txt')
                          ),
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope', 'zope.app'],

      keywords = "zope3 serialization synchronization",
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'],

      tests_require = ['zope.testing'],
      extras_require = dict(
        app = ['zope.app.appsetup',
               'zope.app.authentication',
               'zope.app.component',
               'zope.app.container',
               'zope.app.error',
               'zope.app.form',
               'zope.app.publisher',
               'zope.app.publication',
               'zope.app.security',
               'zope.app.securitypolicy',
               'zope.app.twisted',
               'zope.app.wsgi',
               ]
              ),
      install_requires=['setuptools',
                        'paramiko',
                        'zope.dublincore',
                        'zope.fssync >= 3.5',
                        'zope.i18nmessageid',
                        'zope.interface',
                        'zope.proxy',
                        'zope.testbrowser',
                        'zope.traversing',
                        'zope.xmlpickle',
                        'zope.app.catalog',
                        'zope.app.component',
                        'zope.app.dtmlpage',
                        'zope.app.file',
                        'zope.app.folder',
                        'zope.app.module',
                        'zope.app.securitypolicy',
                        'zope.app.zcmlfiles',
                        'zope.app.zptpage'
                        ],
      include_package_data = True,

      zip_safe = False,
      )
