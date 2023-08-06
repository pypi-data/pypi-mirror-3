# Copyright (c) 2012 Sebastian Wehrmann
# See also LICENSE.txt

import os.path
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name='sw.nikeplus',
    version='0.1',
    url='https://bitbucket.org/sweh/sw.nikeplus',
    license='ZPL 2.1',
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent'],
    description='API for retrieving workout data from Nike+.',
    long_description = (read('README.txt')
                         + '\n\n' +
                         read('src', 'sw', 'nikeplus', 'nikeplus.txt')
                         + '\n\n' +
                         read('CHANGES.txt')
    ),
    author='Sebastian Wehrmann',
    author_email='sebastian.wehrmann@me.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['sw',],
    include_package_data=True,
    install_requires=[
        'httplib2',
        'lxml',
        'setuptools',
        'simplejson',
    ],
    extras_require={
        'test': [
            'mock',
        ],
    },
    zip_safe=True,
    )
