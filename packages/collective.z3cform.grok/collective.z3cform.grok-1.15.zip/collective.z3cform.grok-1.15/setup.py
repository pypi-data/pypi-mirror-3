import os, sys

from setuptools import setup, find_packages

version = '1.15'

def read(*rnames):
    return open(
        os.path.join('.', *rnames)
    ).read()

long_description = "\n\n".join(
    [read('README.txt'),
     read('src', 'collective', 'z3cform', 'grok', 'tests', 'form.txt'), 
     read('docs', 'INSTALL.txt'),
     read('docs', 'HISTORY.txt'),
    ]
)

if 'RST_TEST' in os.environ:
    print long_description
    sys.exit(0) 

classifiers = [
    "Programming Language :: Python",
    "Topic :: Software Development",
    "Framework :: Plone",
    "Programming Language :: Zope",
    "Framework :: Zope2",
    "Framework :: Zope3",
    "Topic :: Software Development :: Libraries :: Python Modules",]

setup(
    name='collective.z3cform.grok',
    namespace_packages=['collective', 'collective.z3cform', 'collective.z3cform.grok',],
    version=version,
    description='A small integration of z3cform using grok magic on plone by Makina Corpus.',
    long_description=long_description,
    classifiers=classifiers,
    keywords='',
    author='Mathieu Pasquet',
    author_email='kiorky@cryptelium.net',
    url='http://svn.plone.org/svn/collective/collective.z3cform.grok',
    license='GPL',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    install_requires=[
        'setuptools',
        'five.grok',
        'plone.z3cform',
        'plone.app.z3cform',
        'z3c.form',
        'martian',
        'grokcore.view', 
        # -*- Extra requirements: -*-
    ],
)
# vim:set ft=python:
