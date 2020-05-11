#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', 'eyeD3>=0.9.5', 'pydantic>=1.5.1', 'requests>=2.23.0',
                'prettytable>=0.7.2', 'python-dateutil>=2.8.1']

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Allen Shaw",
    author_email='lonsty@sina.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A CLI tool to download music of Jay Chou and other singers with full song tags.",
    entry_points={
        'console_scripts': [
            'musicftdl=musicftdl.cli:cli',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='musicftdl',
    name='musicftdl',
    packages=find_packages(include=['musicftdl', 'musicftdl.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/lonsty/musicftdl',
    version='0.1.0',
    zip_safe=False,
)
