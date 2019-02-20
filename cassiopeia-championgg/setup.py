#!/usr/bin/env python

from setuptools import setup, find_packages


install_requires = [
]

setup(
    name="cassiopeia-championgg",
    version="1.0.7",
    author="Jason Maldonis; Rob Rua",
    author_email="team@merakianalytics.com",
    url="https://github.com/meraki-analytics/cassiopeia-plugins/tree/master/cassiopeia-championgg",
    description="A plugin for the LoL wrapper Cassiopeia to use the champion.gg API.",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Environment :: Web Environment",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Games/Entertainment",
        "Topic :: Games/Entertainment :: Real Time Strategy",
        "Topic :: Games/Entertainment :: Role-Playing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    license="MIT",
    packages=find_packages(),
    zip_safe=True,
    install_requires=install_requires,
    include_package_data=True
)
