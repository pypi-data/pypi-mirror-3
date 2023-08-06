from setuptools import setup, find_packages

"""
Installation
===============
easy_install miniuri
"""
#requires = []

setup( 
    name='miniuri',
    version='0.0.1',
    description='Universal URI parser',

    author = 'Russell Ballestrini',
    author_email = 'russell@ballestrini.net',
    keywords = 'uri url parser',
    url = 'https://bitbucket.org/russellballestrini/miniuri/src/tip/miniuri/miniuri.py',

    platforms=['All'],
    license='Public Domain',

    #install_requires = requires,
    #packages=find_packages(),
    package_dir = {'': 'src'},
    py_modules = ['miniuri'],
    include_package_data=True,
    #zip_safe=False
)

# setup keyword args:
# http://peak.telecommunity.com/DevCenter/setuptools 

# build and upload to pypi with this:
#python setup.py sdist bdist_egg register upload
