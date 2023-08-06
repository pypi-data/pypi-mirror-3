from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
    name='his2h5',
    version=version,
    description="Command line utility to convert beterrn Hamamatsu Image Sequence (.HIS) files and HDF5 files.",
    long_description="""\
    """,
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Rich Wareham',
    author_email='rjw57@cam.ac.uk',
    url='',
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
        'h5py',
        'numpy',
    ],
    entry_points="""
        [console_scripts]
        his2h5 = his2h5.tool:main
    """,
)

# vim:sw=4:sts=4:et
