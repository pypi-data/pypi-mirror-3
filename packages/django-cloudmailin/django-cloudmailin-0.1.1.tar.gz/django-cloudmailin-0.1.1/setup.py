from cloudmailin import __version__
from setuptools import setup, find_packages
import os

f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
readme = f.read()
f.close()

setup(
    name='django-cloudmailin',
    version=__version__,
    description='Client for CloudMailin incoming email service',
    long_description=readme,
    author='Jeremy Carbaugh',
    author_email='jcarbaugh@sunlightfoundation.com',
    url='http://github.com/sunlightlabs/django-cloudmailin/',
    packages=find_packages(),
    package_data={
        'cloudmailin': [
            'test/mail/*.txt',
        ],
    },
    license='BSD License',
    platforms=["any"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Environment :: Web Environment',
    ],
)
