#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

# read requirements
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

test_requirements = requirements

setup(
    name='sclust',
    version='0.1.0',
    description="simple sentence clusterer",
    long_description=readme + '\n\n' + history,
    author="Aron Culotta",
    author_email='aronwc@gmail.com',
    url='https://github.com/aronwc/sclust',
    packages=[
        'sclust',
    ],
    package_data={'sclust': ['requirements.txt']},
    package_dir={'sclust':
                 'sclust'},
    include_package_data=True,
    install_requires=requirements,
    license="ISCL",
    zip_safe=False,
    keywords='sclust',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    entry_points={
        'console_scripts': [
            'sclust = sclust.sclust:main',
            'sclust-summarize = sclust.sclust_summarize:main',
        ],
    },
    test_suite='tests',
    tests_require=test_requirements
)
