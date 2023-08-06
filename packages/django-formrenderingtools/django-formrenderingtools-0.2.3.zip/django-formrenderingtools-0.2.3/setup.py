# coding=utf-8
"""Python packaging."""
import os
from setuptools import setup


def read_relative_file(filename):
    """Returns contents of the given file, which path is supposed relative
    to this module."""
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()


name = 'django-formrenderingtools'
version = read_relative_file('VERSION').strip()
readme = read_relative_file('README')
packages = ['djc']
namespace_packages = packages


setup(name=name,
      version=version,
      description="Template-based rendering of Django forms layouts (not widgets).",
      long_description=readme,
      platforms='Any',
      classifiers = ['Development Status :: 4 - Beta',
                     'License :: OSI Approved :: BSD License',
                     'Operating System :: OS Independent',
                     'Framework :: Django',
      ],
      keywords='templates forms layout',
      author='Benoit Bryon',
      author_email='benoit@marmelune.net',
      license='BSD',
      url='http://bitbucket.org/benoitbryon/django-formrenderingtools',
      download_url='http://bitbucket.org/benoitbryon/django-formrenderingtools/downloads',
      packages=packages,
      namespace_packages=namespace_packages,
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'django>=1.0',
                        'django-templateaddons>=0.1'
      ],
      entry_points={},
)
