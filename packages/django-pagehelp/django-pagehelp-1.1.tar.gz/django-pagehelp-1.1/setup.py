#!/usr/bin/env python
from distutils.core import setup

setup(name='django-pagehelp',
      version='1.1',
      description="A Django application which provides contextual help for "
        "your site's pages.",
      author='Chris Beaven',
      author_email='smileychris@gmail.com',
      url='http://bitbucket.org/smileychris/django-pagehelp/',
      packages=[
          'pagehelp',
      ],
      package_data={'pagehelp': ['templates/*', 'static/pagehelp/*']},
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Framework :: Django',
      ],
)
