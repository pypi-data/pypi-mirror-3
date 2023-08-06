# -*- coding: utf-8 -*-
import sys
from setuptools import setup, find_packages
from os.path import join as pathjoin

VERSION = '0.4.1'

LONG_DESCRIPTION = ''.join([
    open(pathjoin('src', 'README')).read()])

CLASSIFIERS = [
    'Environment :: Web Environment',
    "Development Status :: 4 - Beta",
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Topic :: Internet',
]

if sys.version_info < (2, 6):
    unsupported = '''
    pyrtm needs python >= 2.6 or 3.x
    use pyrtm-0.3 if you want to use older version
    '''
    print(unsupported)
    sys.exit(0)

setup(
    name='pyrtm',
    version=VERSION,
    description='Remember The Milk API',
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    author='Sridhar Ratnakumar',
    author_email='pyrtm@srid.name',
    url='http://bitbucket.org/srid/pyrtm/',
    license='MIT License',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={'': ['buildout.cfg']},
    include_package_data=True,
    extras_require=dict(
        test=[
            'Nose',
            'pep8',
        ],
    ),
    test_suite='nose.collector',
    tests_require=['Nose', 'pep8'],
    entry_points="""
       [console_scripts]
       rtm_appsample = rtm.samples.app:main
    """,
)
