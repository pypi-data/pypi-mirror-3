#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='formgear',
      version='0.3',
      description='Form, mongodbengine objects',
      author='Mikhail Kashkin',
      author_email='mkashkin@gmail.com',
      url='https://github.com/xen/formgear',
      # more examples here http://docs.python.org/distutils/examples.html#pure-python-distribution-by-package
      packages=['formgear', ],
      license = "BSD",
      install_requires=[
          'jinja2',
          'python-dateutil == 1.5',
      ],
      package_data = {
        'formgear': [
            'templates/*.html',
            'templates/widgets/*.html',
        ]
    }
     )
