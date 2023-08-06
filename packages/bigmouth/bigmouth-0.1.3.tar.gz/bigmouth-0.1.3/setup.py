# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

__version__ = '0.1.3'

with open('README') as fd:
    README = fd.read()

requires = [
    'setuptools',
    'django',
]

setup(
        name="bigmouth",
        version=__version__,
        description="Django interface to the Pelican static blog generator.",
        long_description=README,
        author="Djerd Flanagan",
        author_email="gflanagan@devopsni.com",
        classifiers=["Development Status :: 1 - Planning",
                    "Intended Audience :: Developers",
                    "License :: OSI Approved :: BSD License",
                    "Programming Language :: Python",
                    "Topic :: Software Development :: Libraries",
                    "Topic :: Software Development :: Libraries :: Python Modules",
                    ],
        license="BSD",
        url="https://github.com/devopsni/django-bigmouth",
        download_url="http://pypi.python.org/packages/source/b/bigmouth/bigmouth-%s.tar.gz" % __version__,
        packages = find_packages('src'),
        package_dir = {'': 'src'},
        install_requires=requires,
      )
    

