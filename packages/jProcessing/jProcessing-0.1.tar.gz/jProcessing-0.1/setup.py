import os
from setuptools import setup, find_packages
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
setup(
    name = 'jProcessing', #First Level Dir
    version='0.1',
    author='KATHURIA Pulkit',
    author_email='pulkit@jaist.ac.jp',
    packages= find_packages('src'),
    #scripts = ['scripts/*.*'],
    package_dir = {'':'src'},
    package_data = {'': ['data/*'],
    },
    include_package_data = True,
    exclude_package_data = {'': ['jNlp/*.p']},
    url='http://www.jaist.ac.jp/~s1010205',
    license='LICENSE.txt',
    description='Japanese NLP Utilities',
    long_description=open('README').read(),
    classifiers=['Development Status :: 2 - Pre-Alpha','Natural Language :: Japanese',
                 'Topic :: Scientific/Engineering :: Artificial Intelligence',
                 'Programming Language :: Python :: 2.6'],
)

"""
Heirarchy
=========
jNlp/
    setup.py
    README
    LICENCE.txt
    scripts/
      ...
    src/
      jNlp/
          __init__.py
          jCabocha.py #see foo.py to check how to access somefile.dat
          jTokenize.py
          data/
            katakanaChart.txt
            hiraganaChart.txt
            edict dictionary files *not included*
          jnlp/
            *not with this package*#see MANIFEST.in
              ...
"""
