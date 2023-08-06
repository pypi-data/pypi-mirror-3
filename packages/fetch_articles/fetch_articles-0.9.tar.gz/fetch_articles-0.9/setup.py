# -*- encoding:utf-8 -*-
#"""
#供py2exe使用
#
#python setup.py py2exe
#"""
#from distutils.core import setup
#import py2exe
#
#setup(console=['win_fa_cmd.pyw'])

from distutils.core import setup

setup(name='fetch_articles',
      version='0.9',
      description='Fetch library articles from cnki when the url is provided. ',
      author='luoboiqingcai',
      author_email='sf.cumt@163.com',
      url='https://bitbucket.org/luoboiqingcai/calculator',
      license='MIT',
      package_dir={'fetch_articles':''},
      packages=['fetch_articles','fetch_articles.tests'],
      scripts=['fa_cmd.py','win_fa_cmd.pyw'],
      classifiers=[
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Operating System :: OS Independent",
          "Intended Audience :: Developers",
          "Intended Audience :: Education",
          "Intended Audience :: End Users/Desktop"
      ]
     )
