from setuptools import setup, find_packages
import os

version = '0.2'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name='slc.autocategorize',
    version=version,
    description="Automatically inherit the parent folder's categories when you "
    "create an object.",
    long_description = (
        read('README.txt')
        + '\n' +
        read("slc", "autocategorize", "README.txt")
        + '\n' +
        read("docs", "HISTORY.txt")
        ),
    # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
    "Framework :: Plone",
    "Programming Language :: Python",
    "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='',
    author='JC Brand, Syslab.com GmbH',
    author_email='brand@syslab.com',
    url='http://svn.plone.org/svn/plone/plone.example',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['slc'],
    include_package_data=True,
    zip_safe=False,
    extras_require={
    'test': 'interlude',
    },
    install_requires=[
        'setuptools',
        'Products.CMFPlone',
    ],
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
    setup_requires=["PasteScript"],
    paster_plugins = ["ZopeSkel"],
    )
