# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

import os


version = "3.6.dev0"


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
        "Framework :: Plone",
        "Framework :: Plone :: 5.0",
        "Framework :: Plone :: 5.1",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: Addon",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
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
        "Products.CMFPlone >= 5.0",
        "plone.app.contenttypes",
    ],
    extras_require={
        "geolocation": [
            # support for latitude/longitude catalog index
            "collective.geolocationbehavior >= 1.6.0",
            # refactored map configuration
            'plone.formwidget.geolocation >= 2.2.0',
            # AJAX geoJSON feature
            'plone.patternslib >= 1.2.2',
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
