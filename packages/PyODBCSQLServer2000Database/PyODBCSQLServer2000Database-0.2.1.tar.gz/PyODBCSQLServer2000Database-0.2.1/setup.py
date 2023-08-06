try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import sys, os

version = '0.2.1'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    "PyODBCSQLServer2000Database\n"
    "+++++++++++++++++++++++++++\n\n"
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
    name='PyODBCSQLServer2000Database',
    version=version,
    description="SQL Server 2000 driver for the DatabasePipe package via ODBC",
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
    url='http://jimmyg.org/work/code/pyodbcsqlserver2000database/index.html',
    license='GNU AGPLv3',
    packages=find_packages(exclude=['ez_setup', 'example', 'test']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
    ],
    extras_require={
        'test': [
            "Database>=2.2.0,<=2.2.99",
        ],
    },
    entry_points="""
        [database.engine]
        insert_record=pyodbcsqlserver2000database.helper:insert_record
        engine_name=  pyodbcsqlserver2000database:engine_name
        plugin_name=  pyodbcsqlserver2000database:plugin_name
        driver_name=  pyodbcsqlserver2000database:driver_name
        param_style=  pyodbcsqlserver2000database:param_style
        update_config=pyodbcsqlserver2000database.helper:update_config
    """,
)
