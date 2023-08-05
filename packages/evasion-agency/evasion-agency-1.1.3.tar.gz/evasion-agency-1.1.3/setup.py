"""
Project's setuptool configuration.

This should eggify and in theory upload to pypi without problems.

Oisin Mulvihill
2008-12-23

"""
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


Name='evasion-agency'
ProjecUrl="http://github.com/oisinmulvihill/evasion-agency/tarball/master#egg=evasion_agency"
Version='1.1.3'
Author='Oisin Mulvihill'
AuthorEmail='oisinmulvihill at gmail dot com'
Maintainer=' Oisin Mulvihill'
Summary='This provides the hardware abstraction layer communicated with via the event system'
License='Evasion Project CDDL License'
ShortDescription=Summary
Description=Summary

TestSuite = 'evasion.agency.tests'

needed = [
    'Mako',
    'configobj',
    'pydispatcher',
]


# Include everything under agency. I needed to add a __init__.py
# to each directory inside agency I did this using the following
# handy command:
#
#  find lib/agency -type d -exec touch {}//__init__.py \;
#
# If new directories are added then I'll need to rerun this command.
#
EagerResources = [
    'evasion',
]

ProjectScripts = [
    'scripts/manager',
]

PackageData = {
    # Include every file type in the egg file:
    '': ['*.*'],
}

# Make exe versions of the scripts:
EntryPoints = {
    'console_scripts': [
        'manager = evasion.agency.scripts.manager:main',
    ]
}


setup(
    url=ProjecUrl,
    zip_safe=False,
    name=Name,
    version=Version,
    author=Author,
    author_email=AuthorEmail,
    description=ShortDescription,
    long_description=Description,
    license=License,
    test_suite=TestSuite,
    scripts=ProjectScripts,
    install_requires=needed,
    packages=find_packages('lib'),
    package_data=PackageData,
    package_dir = {'': 'lib'},
    eager_resources = EagerResources,
    entry_points = EntryPoints,
    namespace_packages = ['evasion'],
)
