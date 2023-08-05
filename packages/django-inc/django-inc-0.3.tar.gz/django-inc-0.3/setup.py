# -*- coding: utf-8 -*-
# Copyright (C) 2011 Pythonheads, all rights reserved.

from distutils.core import setup

long_description = '''
The default {% include %} tag is pretty limited. This inclusion tag is 
different: its flexible and usable for almost any inclusion purpose. 
Also, the designers you work with will love it!
'''

setup(name='django-inc',
      version='0.3',
      packages=['inc', 'inc.templatetags'],
      package_dir={'': 'src'},
      description='A more usable include tag for Django',
      long_description=long_description,
      author='Niels Wijk',
      author_email='niels@pythonheads.nl',
      license='MIT',
      url='http://github.com/pythonheads/inc')

