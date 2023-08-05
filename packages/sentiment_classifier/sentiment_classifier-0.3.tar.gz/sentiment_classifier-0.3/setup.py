import os
from setuptools import setup, find_packages
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
setup(
    name = 'sentiment_classifier', 
    version='0.3',
    author='KATHURIA Pulkit',
    author_email='pulkit@jaist.ac.jp',
    packages= find_packages('src'), 
    scripts = ['scripts/senti_classifier'],
    package_dir = {'':'src'},
    package_data = {'senti_classifier': ['data/*.*'],
    },
    include_package_data = True,
    url='',
    license='LICENSE.txt',
    description='Sentiment Classification using Word Sense Disambiguation and Senti Word Net',
    long_description=open('README.txt').read(),
    classifiers=['Development Status :: 4 - Beta'],
    
)

"""
Structure
=========
sentiment_classifier/
    setup.py
    README.txt
    LICENCE.TXT
    scripts/
      senti_classifier
    src/
      senti_classifier/
          __init__.py
          senti_classifier.py
          data/
              sample_review.txt
"""
