#!/usr/bin/env python3
"""
Setup script for lyrics-cli
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r', encoding='utf-8') as f:
        return f.read()

setup(
    name='lyrics-cli',
    version='1.0.0',
    description='🎵 A command-line tool to search and download song lyrics',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='archboyknm',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/lyrics-cli',
    license='MIT',
    
    # Package configuration
    packages=find_packages(),
    py_modules=['lyrics_fetcher', 'main'],
    
    # Dependencies
    install_requires=[
        'requests>=2.25.0',
    ],
    
    # Python version requirement
    python_requires='>=3.6',
    
    # Entry points for CLI commands
    entry_points={
        'console_scripts': [
            'lyrics-cli=main:main',
            'lyrics=main:main',  # Shorter alias
        ],
    },
    
    # Classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Utilities',
        'Environment :: Console',
    ],
    
    # Keywords
    keywords='lyrics music songs cli command-line download',
    
    # Project URLs
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/lyrics-cli/issues',
        'Source': 'https://github.com/yourusername/lyrics-cli',
        'Documentation': 'https://github.com/yourusername/lyrics-cli/README.md',
    },
)

##### bash script remaining