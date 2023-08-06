import os
from setuptools import setup, find_packages

# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "assembla",
    version = "1.1.1",
    packages = find_packages(),

    install_requires = [
        'requests>=0.7.4',
        'lxml>=2.3.1',
    ],

    package_data = {
        'assembla': [
        ]
    },

    entry_points = {
    },

    # metadata for upload to PyPI
    author = "Mark Finger",
    author_email = "markfinger@gmail.com",
    description = (
        "Python wrapper for the Assembla API"
    ),
    license = "BSD",
    platforms=['any'],
    keywords = "Assembla API",
    url = "https://github.com/markfinger/assembla/",
    long_description = read('README.rst'),
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Operating System :: OS Independent",
        'Programming Language :: Python',
        "License :: OSI Approved :: BSD License",
    ],
)
