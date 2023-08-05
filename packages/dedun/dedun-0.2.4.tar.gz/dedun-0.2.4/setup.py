# *-* encoding: utf-8 *-*
import os
from setuptools import setup

def read(*path):
    basepath = os.path.abspath(os.path.dirname(__file__))
    return open(os.path.join(basepath, *path)).read()

setup(name='dedun',
    version=':versiontools:dedun:',
    url='https://bitbucket.org/keimlink/dedun',
    author='Markus Zapke-Gruendemann',
    author_email='info@keimlink.de',
    description='Dedun is a Python client for the RESTful API of API.Leipzig. This API gives access to the public data of the city of Leipzig.',
    long_description=read('README.rst') + '\n\n' + read('CHANGELOG.rst'),
    license='MIT License',
    py_modules=['dedun'],
    install_requires=['anyjson'],
    classifiers=['Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries'
    ]
)
