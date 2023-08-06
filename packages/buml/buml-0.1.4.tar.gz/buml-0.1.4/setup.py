from setuptools import setup, find_packages
import sys, os

version = '0.1.4'

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='buml',
      version=version,
      description="buml markup language",
      long_description=read('README'),
      classifiers=['Development Status :: 4 - Beta', 
                   'Environment :: Console',
                   'Environment :: Web Environment', 
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Text Processing :: Markup',
                   'Topic :: Text Processing :: Markup :: XML',
                   'Topic :: Text Processing :: Markup :: HTML',
                   'Topic :: Text Processing' 
                   ],
      keywords='buml xml html nodeTree shpaml template',
      author='Bud P. Bruegger',
      author_email='bud@bruegger.it',
      url='http://bruegger.it/buml/',
      license='FreeBSD',
      packages=['buml', 'tests'],
      scripts=['bin/b2x', 'bin/bi2x'],
      data_files=['testData/demo.buml', 'testData/inlineDemo.buml'],
      include_package_data=True,
      zip_safe=True
      )
