import os
from setuptools import setup, find_packages

tests_require = [
    'martian',
    'grokcore.component',
    'zope.annotation',
    'zope.app.appsetup',
    'zope.app.pagetemplate',
    'zope.app.publication',
    'zope.app.wsgi >= 3.10.0',
    'zope.browserpage',
    'zope.browserresource',
    'zope.container',
    'zope.contentprovider',
    'zope.login',
    'zope.password',
    'zope.principalregistry',
    'zope.security',
    'zope.securitypolicy',
    ]

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='grokui.base',
      version='0.7',
      description="The Grok administration and development UI (base)",
      long_description=(
        read('README.txt') +
        '\n\n' +
        read(os.path.join('src', 'grokui', 'base', 'README.txt')) +
        '\n\n' +
        read('CHANGES.txt')
        ),
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
      keywords="zope3 grok grokadmin",
      author="Zope Foundation and Contributors",
      author_email="grok-dev@zope.org",
      url="http://svn.zope.org/grokui.base",
      license="ZPL 2.1",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      namespace_packages = ['grokui'],
      install_requires=[
          'fanstatic',
          'grok >= 1.10',
          'grokcore.layout >= 1.5',
          'grokcore.message',
          'megrok.menu',
          'setuptools',
          'zope.authentication',
          'zope.browsermenu',
          'zope.component',
          'zope.fanstatic',
          'zope.interface',
          'zope.location',
          'zope.publisher',
          'zope.site',
          'zope.traversing',
          ],
      tests_require = tests_require,
      extras_require = dict(test=tests_require),
      entry_points={
          'fanstatic.libraries': [
              'grokui.base = grokui.base.resource:library']}
      )
