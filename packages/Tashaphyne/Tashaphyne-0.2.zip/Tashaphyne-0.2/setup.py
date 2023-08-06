#! /usr/bin/python
from distutils.core import setup
from glob import glob

# to install type:
# python setup.py install --root=/

setup (name='Tashaphyne', version='0.2',
      description='Tashaphyne Arabic Light Stemmer and segmentor',
      author='Taha Zerrouki',
      author_email='taha_zerrouki@gawab.com',
      url='http://tashaphyne.sourceforge.net/',
      license='GPL',
      # Description="Arabic Light Stemmer and segmentor",
      # Platform="OS independent",
      package_dir={'tashaphyne': 'tashaphyne',},
      packages=['tashaphyne'],
      # include_package_data=True,
      package_data = {
        'tashaphyne': ['doc/*.*','doc/html/*'],
        },
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: End Users/Desktop',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python',
          ],
    );

