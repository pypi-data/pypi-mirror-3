# installation: easy_install miniuri

from setuptools import setup

setup( 
    name='miniuri',
    version='0.0.2',
    long_description = open('README').read(),
    description='miniuri: The Universal URI Parser',
    keywords = 'miniuri uri url parser',

    author = 'Russell Ballestrini',
    author_email = 'russell@ballestrini.net',
    url = 'https://bitbucket.org/russellballestrini/miniuri/src',

    platforms=['All'],
    license='Public Domain',

    py_modules = ['miniuri'],
    include_package_data=True,
)

# setup keyword args: http://peak.telecommunity.com/DevCenter/setuptools 

# built and uploaded to pypi with this:
#python setup.py sdist bdist_egg register upload
