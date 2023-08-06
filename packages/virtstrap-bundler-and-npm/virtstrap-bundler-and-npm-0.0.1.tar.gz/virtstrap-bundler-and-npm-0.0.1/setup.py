from setuptools import setup, find_packages
import sys, os


version = '0.0.1'

setup(
    name='virtstrap-bundler-and-npm',
    version=version,
    description="A virtstrap plugin that installs bundler Gemfiles and nodejs local dependencies",
    long_description="A virtstrap plugin that installs bundler Gemfiles and nodejs local dependencies",
    classifiers=[],
    keywords='virtstrap ruby bundler nodejs npm virtualenv pip',
    author='Mattias Wong',
    author_email='0x1998@gmail.com',
    url='',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'virtstrap-local',
    ],
    entry_points={
        'virtstrap_local.plugins': [
            'sample = virtstrap_bundler_and_npm.plugin',
        ]
    },
)
