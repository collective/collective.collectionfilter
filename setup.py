from setuptools import find_packages
from setuptools import setup

import os


version = "5.3.0"


def read(*rnames):
    with open(os.path.join(os.path.dirname(__file__), *rnames)) as f:
        return f.read()


setup(
    name="collective.collectionfilter",
    version=version,
    description="Plone addon for filtering collection results.",
    long_description="{}\n\n{}".format(
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
        "Programming Language :: Python :: 3.11",
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
    python_requires=">=3.8",
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        "plone.api >= 2.0.0",
        "plone.app.contenttypes",
        "plone.app.event",
        "plone.app.querystring",
        "plone.app.uuid",
        "plone.app.vocabularies",
        "plone.app.z3cform",
        "plone.autoform",
        "plone.base",
        "plone.dexterity",
        "plone.i18n",
        "plone.memoize",
        "plone.portlets",
        "plone.supermodel",
        "plone.uuid",
        "z3c.form",
        "Products.CMFCore",
        "Products.CMFPlone >= 6.0",
    ],
    extras_require={
        "mosaic": [
            "plone.app.mosaic >= 3.0.0",
        ],
        "geolocation": [
            # support for latitude/longitude catalog index
            "collective.geolocationbehavior >= 1.7.2",
            # refactored map configuration
            "plone.formwidget.geolocation >= 3.0.0",
        ],
        "test": [
            "plone.app.mosaic",
            "plone.browserlayer",
            "plone.testing",
            "robotsuite",
            "collective.geolocationbehavior",
            "plone.app.testing[robot]",
            "plone.app.robotframework",
            "plone.app.contenttypes",
            "plone.app.portlets",
            "plone.app.textfield",
            "plone.tiles",
        ],
    },
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
