'''
Created on Mar 6, 2012

@author: brian
'''
from setuptools import setup, find_packages
 
version = '0.1.6.4'
 
LONG_DESCRIPTION = """
======================================
Leaner (Django Lean Startup Framework)
======================================

This project was inspired by "The Lean Startup" by Eric Ries and django-lean.
The goal is to provide an easy way for Django apps to test new ideas and features in a 
non-disruptive way.  

"""
 
setup(
    name='leaner',
    version=version,
    description="""This project was inspired by "The Lean Startup" by Eric Ries "
    "and django-lean. The goal is to provide an easy way for Django apps to "
    "test new ideas and features in a non-disruptive way.""",
    long_description=LONG_DESCRIPTION,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Web Environment",
    ],
    keywords='test,django,lean startup,web',
    author='Brian Jinwright',
    author_email='team@ipoots.com',
    maintainer='Brian Jinwright',
    packages=('leaner','leaner.goalrecord','leaner.templatetags','leaner.tests',
              'leaner_rel_db'),
    url='https://bitbucket.org/brianjinwright/leaner',
    license='Apache',
    install_requires=['Django>=1.3.1','South>=0.7.3',
        'django-classy-tags>=0.3.4.1','gargoyle==0.8.0',
        'boto==2.3.0','mock==0.8.0','Unipath==0.2.1'],
    include_package_data=True,
    zip_safe=False,
)
