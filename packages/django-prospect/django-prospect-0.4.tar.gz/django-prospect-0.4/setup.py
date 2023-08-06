# -*- coding: utf-8 -*-
import codecs
import re
from os import path
from distutils.core import setup
from setuptools import find_packages


def read(*parts):
    return codecs.open(path.join(path.dirname(__file__), *parts)).read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='django-prospect',
    version=find_version('prospect', '__init__.py'),
    author=u'Ionyse',
    author_email='support@ionyse.com',
    packages=find_packages(),
    include_package_data=True,
    url='http://bitbucket.org/ionyse/django-prospect',
    license='LGPL licence, see LICENSE file',
    description='Managing your prospects easily',
    long_description=read('README.rst'),
    install_requires=[
        'django-intranet',
        'xlrd',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    zip_safe=False,
)
