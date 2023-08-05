import sys, os
try:
    from setuptools import setup, find_packages
except ImportError:
    print "You need to install the setuptools module to install this software"

version = '0.1.0'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    "logrotate\n"
    "+++++++++\n\n"
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
    name='logrotate',
    version=version,
    description="A small, simple logrotate implementation for the Python logging module that only rotates files (it doesn't create and delete them) and therefore maintains owner, group and permission information",
    long_description=long_description,
    # Get classifiers from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        #'Environment :: Web Environment',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python',
    ],
    keywords='',
    author='James Gardner',
    author_email='',
    url='http://jimmyg.org',
    license='MIT',
    packages=find_packages(exclude=['example', 'test']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
    ],
    extras_require={
    },
    entry_points="""
    """,
)
