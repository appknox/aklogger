import os

from setuptools import setup, find_packages

__VERSION__ = '0.0.1a1'


def readme(*paths):
    with open(os.path.join(*paths), 'r') as f:
        return f.read()


setup(
    name="aklogger",
    version=__VERSION__,
    author="appknox",
    author_email="engineering@appknox.com",
    description="A generic logging package for python projects",
    long_description=readme('README.md'),
    url="https://github.com/appknox/aklogger",
    packages=find_packages(),
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'slacker>=0.7.3,<=0.9.65',
        'six==1.11.0'
    ],
    extras_require={
        'dev': [
            'bumpversion==0.5.3',
            'twine==1.12.1',
            'flake8==3.7.7'
        ],
        'test': [
            'codecov==2.0.15',
            'coverage==4.5.2',
            'pytest-cov==2.6.1'
        ],
    },
    keywords='appknox aklogger',
    entry_points='',
)
