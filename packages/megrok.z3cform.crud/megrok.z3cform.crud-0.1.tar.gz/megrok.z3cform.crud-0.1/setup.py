from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='megrok.z3cform.crud',
      version=version,
      description="Crud forms for Grok, uusing z3c.form",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Zope3",
        "Programming Language :: Python",
        ],
      keywords='Grok CRUD z3c.form',
      author='Danilo G. Botelho',
      author_email='danilogbotelho@yahoo.com',
      url='http://pypi.python.org/pypi/megrok.z3cform.crud',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['megrok', 'megrok.z3cform'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'grokcore.view',
          'grokcore.component',
          'z3c.batching',
          'z3c.form>=2.1',
          'megrok.z3cform.base',
      ],
      entry_points="""""",
      )
