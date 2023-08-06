from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='pas.plugins.external_auth',
      version=version,
      description="A plugin to allow external authentication informations "
                  "(commonly headers from apache to work with most SSO) to "
                  "create users and groups.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read() +
                       open(os.path.join("docs", "INSTALL.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Zope2',
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU General Public License v3 or later ' \
                                  '(GPLv3+)',
        'Operating System :: OS Independent',
        ],
      keywords='Zope Authentication SSO Shibboleth PluggableAuthService',
      author='Maric Michaud',
      author_email='maric.michaud@smile-suisse.com',
      url='http://www.smile-suisse.com/',
      #url='https://github.com/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      package_data={'external_auth': ['*.pt', 'profiles/*', '*.zcml']},
      namespace_packages=['pas', 'pas.plugins'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.PluggableAuthService',
          'pas.cmfextensions.update_steps'
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
