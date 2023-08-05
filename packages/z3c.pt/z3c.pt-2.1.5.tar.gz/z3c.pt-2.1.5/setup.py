from setuptools import setup, find_packages
import sys

version = '2.1.5'

install_requires = [
    'setuptools',
    'zope.interface',
    'zope.component',
    'zope.i18n >= 3.5',
    'zope.traversing',
    'zope.contentprovider',
    'Chameleon >= 2.4.0',
    ]

setup(name='z3c.pt',
      version=version,
      description="Fast ZPT engine.",
      long_description=open("README.txt").read() + open("CHANGES.txt").read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: XML",
        ],
      keywords='',
      author='Malthe Borch and the Zope Community',
      author_email='zope-dev@zope.org',
      url='',
      license='ZPL',
      namespace_packages=['z3c'],
      packages = find_packages('src'),
      package_dir = {'':'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      )
