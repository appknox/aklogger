import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="varys",
    version="0.0.1",
    author="Shrikrishna Singh",
    author_email="shrikrishna@appknox.com",
    description="A generic logging package for python projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/varys",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

