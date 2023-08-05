#!/usr/bin/env python

from setuptools import setup, find_packages
setup(name='django-admin-skel',
      version='1.0.7',
      description='Basic admin styles for django (non django.contrib.admin). Maintained by Alexey Loshkarev <alexey@smscoin.com>',
      author='Andrey Shuster',
      author_email='andrey@smscoin.com',
      url='http://pypi.python.org/pypi/django-admin-skel/',
      packages=find_packages(),
      license='GPL',
      classifiers=[
          "Development Status :: 5 - Production/Stable", 
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Natural Language :: English",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      zip_safe=False,
      include_package_data=True,
      )
