# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

import os


version = "5.0a2"


def read(*rnames):
    with open(os.path.join(os.path.dirname(__file__), *rnames)) as f:
        return f.read()


setup(
    name="collective.collectionfilter",
    version=version,
    description="Plone addon for filtering collection results.",
    long_description="{0}\n\n{1}".format(
        read("README.rst"),
        read("CHANGES.rst"),
    ),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Addon",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="plone collection filter faceted tagcloud tags",
    author="Johannes Raggam",
    author_email="thetetet@gmail.com",
    url="http://github.com/collective/collective.collectionfilter",
    license="GPL",
    namespace_packages=[
        "collective",
    ],
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        "plone.api >= 1.5.1",
        "Products.CMFPlone >= 5.2",
        "plone.app.contenttypes",
    ],
    extras_require={
        "mosaic": [
            "plone.app.mosaic >= 2.2.3",
            "plone.app.standardtiles >= 2.4.0",
        ],
        "geolocation": [
            # support for latitude/longitude catalog index
            "collective.geolocationbehavior >= 1.6.0",
            # refactored map configuration
            "plone.formwidget.geolocation >= 2.2.0",
            # leaflet JS events for map filter
            "plone.patternslib >= 1.1.0",
        ],
        "test": [
            "plone.app.mosaic",
            "collective.geolocationbehavior",
            "plone.app.testing[robot]",
            "plone.app.robotframework",
            "plone.app.contenttypes",
            "robotframework-selenium2library",
            "robotframework-selenium2screenshots",
        ],
    },
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
