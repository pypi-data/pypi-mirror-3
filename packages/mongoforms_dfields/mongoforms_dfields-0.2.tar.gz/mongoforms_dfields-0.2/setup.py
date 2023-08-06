# encoding: utf-8
import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='mongoforms_dfields',
    version='0.2',
    description='A ModelForm-DynamicFields',
    author=u'Luís Araújo',
    author_email='luis@multmeio.com.br',
    maintainer=u'Luís Araújo',
    maintainer_email='luis@multmeio.com.br',
    url='https://github.com/multmeio/mongoforms_dfields',
    packages=find_packages(
        exclude=['examples', 'examples.*']),
    # long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    zip_safe=False,
    install_requires=['Django', 
    	'mongoengine>=0.6', 
    	'pymongo>=2.1', 
	    'django_mongoforms>=0.3']
)
