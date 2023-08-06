from setuptools import find_packages
from setuptools import setup

VERSION = '0.0.1'


setup(
    author='Alex Clark',
    author_email='aclark@aclark.net',
    entry_points={
        'z3c.autoinclude.plugin': 'target = plone',
    },
    include_package_data=True,
    name='event_days_indexer',
    packages=find_packages(),
    version=VERSION,
)
