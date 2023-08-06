from setuptools import find_packages
from setuptools import setup
import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


long_description = (
    read('collective', 'portlet', 'contentsearch', 'docs', 'README.rst') + "\n" +
    read('collective', 'portlet', 'contentsearch', 'docs', 'HISTORY.rst') + "\n" +
    read('collective', 'portlet', 'contentsearch', 'docs', 'CONTRIBUTORS.rst'))


setup(
    name='collective.portlet.contentsearch',
    version='0.2',
    description="Adds content search portlet for Plone..",
    long_description=long_description,
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7"],
    keywords='',
    author='Taito Horiuchi',
    author_email='taito.horiuchi@gmail.com',
    url='https://github.com/collective/collective.portlet.contentsearch',
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['collective', 'collective.portlet'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Plone>=4.1',
        'hexagonit.testing',
        'setuptools',
        'zope.i18nmessageid'],
    entry_points="""
    # -*- Entry points: -*-

    [z3c.autoinclude.plugin]
    target = plone
    """)
