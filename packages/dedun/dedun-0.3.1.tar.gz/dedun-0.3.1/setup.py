# encoding: utf-8
import codecs
import os
import sys

from setuptools import Command, find_packages, setup


reload(sys).setdefaultencoding('UTF-8')


def read(*path):
    basepath = os.path.abspath(os.path.dirname(__file__))
    return codecs.open(os.path.join(basepath, *path), 'r', 'utf-8').read()


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        import sys
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)


setup(name='dedun',
    version=':versiontools:dedun:',
    url='https://bitbucket.org/keimlink/dedun',
    author=u'Markus Zapke-Gründemann',
    author_email='info@keimlink.de',
    cmdclass={'test': PyTest},
    description='Dedun is a Python client for the RESTful API of API.Leipzig. This API gives access to the public data of the city of Leipzig.',
    long_description=read('README.rst') + '\n\n' + read('CHANGELOG.rst'),
    license='BSD License',
    py_modules=['runtests'],
    packages=find_packages(),
    zip_safe=False,
    setup_requires = ['versiontools>=1.8'],
    install_requires=['anyjson>=0.3.1'],
    classifiers=['Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries'
    ]
)
