from setuptools import find_packages
from setuptools import setup

version = '1.3'

setup(
    name='collective.portlet.collectionfilter',
    version=version,
    description="Portlets for filtering collection results.",
    long_description='{0}\n{1}'.format(
        open("README.rst").read(),
        open("CHANGES.rst").read()
    ),
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='plone portlet collection filter faceted tagcloud tags',
    author='Johannes Raggam',
    author_email='johannes@raggam.co.at',
    url='http://github.com/collective/collective.portlet.collectionfilter',
    license='GPL',
    namespace_packages=['collective', 'collective.portlet'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Products.CMFPlone',
    ],
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """
)
