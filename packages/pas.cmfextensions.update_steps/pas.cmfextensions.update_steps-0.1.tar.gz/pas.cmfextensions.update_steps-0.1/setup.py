from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='pas.cmfextensions.update_steps',
      version=version,
      description=".",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Zope2',
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        ],
      keywords='PluggableAuthService GenericSetup',
      author='Maric Michaud',
      author_email='maric.michaud@smile-suisse.com',
      #url='https://github.com/collective/',
      url='https://www.smile-suisse.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      package_data={'': ['docs/*', '*.zcml']},
      namespace_packages=['pas', 'pas.cmfextensions'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.PluggableAuthService',
          'Products.GenericSetup',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
