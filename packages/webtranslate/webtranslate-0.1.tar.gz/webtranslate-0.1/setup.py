#!/usr/bin/env python

from distutils.core import setup

setup(name='webtranslate',
      version='0.1',
      description='Translate html (lxml based) using google translate api',
      author='Victor Gavro',
      author_email='vgavro@gmail.com',
      url='http://bitbucket.org/vgavro/webtranslate',
      packages=['webtranslate'],
      install_requires=['lxml', 'google-translate'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords='translate html text google',
     )
