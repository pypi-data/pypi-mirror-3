#!/usr/bin/env python

from setuptools import setup, find_packages
import os


CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Unix',
    'Operating System :: POSIX',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.5',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Topic :: Communications',
    'Topic :: Communications :: Chat',
    'Topic :: Communications :: Chat :: Internet Relay Chat',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Message Boards',
]


setup(name='django-push2',
      version=__import__('push2').__version__,
      url='https://bitbucket.org/cellarosi/django-push',
      description='Django push engine for web application',
      long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
      author='Cellarosi Marco',
      author_email='cellarosi@gmail.com',
      packages=find_packages(),
      namespace_packages=['push2'],
      include_package_data=True,
      zip_safe=False,
      classifiers=CLASSIFIERS,
      install_requires=[
        'Django==1.3',
        ],
     )
