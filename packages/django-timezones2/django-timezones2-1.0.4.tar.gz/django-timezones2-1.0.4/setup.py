#!/usr/bin/python
from setuptools import setup, find_packages

setup(name='django-timezones2',
      version='1.0.4',
      description="Timezone utilities for Django",

      author='Rafal Stozek',
      author_email='say4ne@gmail.com',
      url="https://bitbucket.org/sayane/django-timezones2",
      classifiers=[
          'Framework :: Django', 'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'Development Status :: 5 - Production/Stable',
      ],
      license='Beer-ware',
      
      packages=find_packages(exclude=('testapp', 'testapp.*',
                                      'project', 'project.*')),
      install_requires=['pytz'],
      requires=['pytz'],
      
      test_suite = "runtests.runtests",
      zip_safe=True
)
