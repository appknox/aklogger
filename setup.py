import os
import setuptools

VERSION = "0.0.1"

def readme(*paths):
    with open(os.path.join(*paths), 'r') as f:
        return f.read()


def requirements(*paths):
    with open(os.path.join(*paths), 'r') as f:
        return list(line.strip() for line in f.readlines() if line.strip() != '')


setuptools.setup(
    name="aklogger",
    version=VERSION,
    author="Shrikrishna Singh",
    author_email="shrikrishna@appknox.com",
    description="A generic logging package for python projects",
    long_description=readme('README.md'),
    url="https://github.com/appknox/aklogger",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements('requirements.txt'),
)
