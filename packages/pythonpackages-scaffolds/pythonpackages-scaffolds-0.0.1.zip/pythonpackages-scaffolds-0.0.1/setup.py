from setuptools import find_packages
from setuptools import setup

VERSION='0.0.1'


setup(
    author='Alex Clark',
    author_email='aclark@aclark.net',
    description='PasteScript paster templates for pythonpackages.com',
    long_description=open('README.md').read() + '\n' +
        open('HISTORY.txt').read(),
    entry_points={
        'paste.paster_create_template':
            'plone_theme = pythonpackages_scaffolds:PloneTheme',
    },
    include_package_data=True,
    install_requires=[
        'PasteScript',
        'ZopeSkel<=2.99.99',
    ],
    name='pythonpackages-scaffolds',
    packages=find_packages(),
    version=VERSION,
    )
