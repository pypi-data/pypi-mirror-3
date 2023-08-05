from setuptools import setup, find_packages
from os.path import join

name = 'dolmen.authentication'
version = '0.3'
readme = open(join('src', 'dolmen', 'authentication', 'README.txt')).read()
history = open(join('docs', 'HISTORY.txt')).read()

setup(name = name,
      version = version,
      description = 'Authentication for Grok applications',
      long_description = readme[readme.find('\n\n'):] + '\n' + history,
      keywords = 'Grok Zope3 Dolmen',
      author = 'Souheil Chelfouh',
      author_email = 'souheil@chelfouh.com',
      url = 'http://www.dolmen-project.org',
      download_url = 'http://pypi.python.org/pypi/dolmen.authentication',
      license = 'GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages = ['dolmen'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      extras_require={'test': [
          ]},
      install_requires=[
          'setuptools',
          'grokcore.component',
          'zope.component',
          'zope.container',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.location',
          'zope.pluggableauth',
          'zope.schema',
          'zope.security',
      ],
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Zope3',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
      ],
)
