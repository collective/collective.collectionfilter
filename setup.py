# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

version = '2.0.2.dev0'

setup(
    name='collective.collectionfilter',
    version=version,
    description="Plone addon for filtering collection results.",
    long_description='{0}\n\n{1}'.format(
        open("README.rst").read(),
        open("CHANGES.rst").read()
    ),
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 5.0",
        "Framework :: Plone :: 5.1",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='plone collection filter faceted tagcloud tags',
    author='Johannes Raggam',
    author_email='thetetet@gmail.com',
    url='http://github.com/collective/collective.collectionfilter',
    license='GPL',
    namespace_packages=['collective', ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Products.CMFPlone >= 5.0',
        'plone.app.contenttypes',
    ],
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """
)
