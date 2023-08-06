#!/usr/bin/env python
"""
Installation script:

To release a new version to PyPi:
- Ensure the version is correctly set in oscar.__init__.py
- Run: python setup.py sdist upload
"""

from setuptools import setup, find_packages

from rss2rest import get_version


setup(name='django-rss2rest',
    version=get_version().replace(' ', '-'),
    url='https://github.com/gump/rss2rest',
    author="Michal Gump Szczesny",
    author_email="gump@gump.tv",
    description="RSS scraper with immediate RESTful access to feed items",
    long_description=open('README.md').read(),
    keywords="Django, RSS, RESTful API",
    license='BSD',
    platforms=['linux'],
    packages=find_packages(exclude=["sandbox*", "tests*"]),
    include_package_data=True,
    install_requires=[
        'django==1.4',
        'django-tastypie==0.9.11',
        'feedparser==5.1.2',
        'python-dateutil==1.5',
        ],
    # See http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=['Environment :: Web Environment',
                 'Framework :: Django',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Operating System :: Unix',
                 'Programming Language :: Python']
)