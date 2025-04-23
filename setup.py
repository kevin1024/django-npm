from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from os import path

here = path.abspath(path.dirname(__file__))

requirements = ['django-appconf']

try:
    from collections import OrderedDict
except ImportError:
    requirements.append('ordereddict')

setup(
    name='django-npm',
    version='1.1.0',
    description='A django staticfiles finder that uses npm',
    url='https://github.com/kevin1024/django-npm',
    author='Kevin McCarthy',
    author_email='me@kevinmccarthy.org',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.9'
    ],

    keywords='django npm staticfiles',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=requirements,
    extras_require={
        'test': ['pytest'],
    },
)
