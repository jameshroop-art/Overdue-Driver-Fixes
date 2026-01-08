#!/usr/bin/env python3
"""
Setup script for driver-mgt
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / 'README.md'
long_description = readme_file.read_text() if readme_file.exists() else ''

setup(
    name='driver-mgt',
    version='1.0.0',
    description='Advanced Linux Driver & Hardware Management System',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='James Hroop',
    url='https://github.com/jameshroop-art/driver-mgt',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.9',
    install_requires=[
        'PyQt6>=6.4.0',
        'psutil>=5.9.0',
        'requests>=2.28.0',
        'pyyaml>=6.0',
    ],
    entry_points={
        'console_scripts': [
            'driver-mgt=driver-mgt:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Topic :: System :: Hardware',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: POSIX :: Linux',
    ],
    keywords='driver hardware management linux nvidia amd wifi',
)
