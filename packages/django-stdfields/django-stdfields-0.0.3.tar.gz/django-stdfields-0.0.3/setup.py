# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='django-stdfields',
    version='0.0.3',
    author=u'Kevin Wetzels',
    author_email=u'kevin@roam.be',
    url='https://bitbucket.org/roam/django-stdfields',
    packages=['stdfields', 'stdfields.templatetags'],
    license='BSD licence, see LICENCE',
    description='Extra model and form fields for Django: minutes and ' + \
                'enumerations',
    long_description=open('README.rst').read(),
    zip_safe=False,
)