from os.path import join, dirname
from setuptools import setup, find_packages


def read(name):
    return open(join(dirname(__file__), name)).read()


setup(
    name="Djserializers",
    version="0.9",
    author="Preston Timmons",
    author_email="prestontimmons@gmail.com",
    description="Serializers for Django",
    long_description=read("README.rst"),
    url = "https://github.com/prestontimmons/serializers/",

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    classifiers= [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Framework :: Django",
        "License :: OSI Approved :: BSD License",
    ],
)
