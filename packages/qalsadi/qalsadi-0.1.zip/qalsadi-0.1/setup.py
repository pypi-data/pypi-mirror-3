#! /usr/bin/python
from distutils.core import setup
from glob import glob

# to install type:
# python setup.py install --root=/

setup (name='qalsadi', version='0.1',
      description='Qalsadi Arabic Morpholoc=gical Analyzer for Python',
      author='Taha Zerrouki',
      author_email='taha. zerrouki@gmail .com',
      url='http://qalsadi.sourceforge.net/',
      license='GPL',
      package_dir={'qalsadi': 'qalsadi',},
      packages=['qalsadi'],
      # include_package_data=True,
      package_data = {
        'qalsadi': ['doc/*.*','doc/html/*', 'data/*.*'],
        },
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: End Users/Desktop',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          ],
    );

