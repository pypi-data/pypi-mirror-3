try:
    from setuptools import setup, find_packages
except ImportError:
    print "You need to install the setuptools module to install this software"

import sys, os

version = '0.1.1'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    "ApacheMiddleware\n"
    "++++++++++++++++\n\n"
    ".. contents :: \n"
    "\n"+read('doc/index.txt')
    + '\n'
    + read('CHANGELOG.txt')
    + '\n'
    'License\n'
    '=======\n'
    + read('LICENSE.txt')
    + '\n'
    'Download\n'
    '========\n'
)

setup(
    name='apachemiddleware',
    version=version,
    description="Useful Python middleware for use with mod_wsgi deployments",
    long_description=long_description,
    # Get classifiers from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        #'Environment :: Web Environment',
        'Programming Language :: Python',
    ],
    keywords='',
    author='James Gardner',
    author_email='james@<package hompage URL>',
    url='http://jimmyg.org/work/code/apachemiddleware/index.html',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'example', 'test']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
    ],
    extras_require={
        'test': [],
    },
    entry_points="""
    """,
)
