from setuptools import setup, find_packages
import sys, os

version = '0.0.1'

LONG_DESCRIPTION = """
A sample plugin for virtstrap. You may use this as a guide to creating a 
plugin. 
"""

setup(
    name='virtstrap-sample-plugin',
    version=version,
    description="A sample plugin for virtstrap",
    long_description=LONG_DESCRIPTION,
    classifiers=[],
    keywords='virtstrap sample plugin',
    author='Reuven V. Gonzales',
    author_email='reuven@tobetter.us',
    url='',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'virtstrap-local', # This is a local plugin so it 
                           # requires virtstrap-local
    ],
    entry_points={
        'virtstrap_local.plugins': [
            'sample = virtstrapsampleplugin.plugin',
        ]
    },
)
