# coding=utf-8
import os.path
from setuptools import setup, find_packages

def read_relative_file(filename):
    """Returns contents of the given file.
    Filename argument must be relative to this module.
    """
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()

setup(
    name='django-formrenderingtools',
    version='0.2.1',
    url='http://bitbucket.org/benoitbryon/django-formrenderingtools',
    download_url='http://bitbucket.org/benoitbryon/django-formrenderingtools/downloads',
    author='Benoit Bryon',
    author_email='benoit@marmelune.net',
    license='BSD',
    description="Template-based rendering of Django forms (excluding widgets).",
    long_description=read_relative_file('README.txt'),
    platforms='Any',
    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Django',
    ],
    packages=find_packages(),
    namespace_packages=['djc'],
    include_package_data = True,
    install_requires=[
        'setuptools',
        'django>=1.0',
        'django-templateaddons>=0.1'
    ],
)
