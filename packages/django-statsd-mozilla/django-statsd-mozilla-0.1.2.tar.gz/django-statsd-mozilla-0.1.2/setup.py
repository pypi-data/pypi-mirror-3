import os
from setuptools import setup


setup(
    # Because django-statsd was taken, I called this django-statsd-mozilla.
    name='django-statsd-mozilla',
    version='0.1.2',
    description='Django interface with statsd',
    long_description=open('README.rst').read(),
    author='Andy McKay',
    author_email='andym@mozilla.com',
    license='BSD',
    packages=['django_statsd',
              'django_statsd/patches',
              'django_statsd/clients'],
    url='https://github.com/andymckay/django-statsd',
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Framework :: Django'
        ],
    )
