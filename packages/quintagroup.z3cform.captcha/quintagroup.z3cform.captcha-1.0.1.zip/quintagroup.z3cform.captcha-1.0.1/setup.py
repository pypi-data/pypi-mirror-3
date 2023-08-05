from setuptools import setup, find_packages
import os

version = '1.0.1'

setup(name='quintagroup.z3cform.captcha',
      version=version,
      description="Captcha field for z3cform based on quintagroup.captcha.core package",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone z3c form captcha',
      author='Quintagroup',
      author_email='support@quintagroup.com',
      url='http://svn.quintagroup.com/products/quintagroup.z3cform.captcha/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['quintagroup', 'quintagroup.z3cform'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'quintagroup.captcha.core',
          'z3c.form',
          # 'zope.schema',
          # 'zope.i18n',
          # 'zope.component',
          # 'zope.interface',
          # 'zope.app.pagetemplate',
          # 'Products.CMFCore',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )


