import os
import re

from setuptools import find_packages, setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def requirements(fname):
    """
    Generator to parse requirements.txt file

    Supports bits of extended pip format (git urls)
    """
    with open(fname) as f:
        for line in f:
            match = re.search('#egg=(.*)$', line)
            if match:
                yield match.groups()[0]
            else:
                yield line.strip()


setup(
    name="ores",
    version="0.5.4", # Update in ores/__init__.py too.
    author="Aaron Halfaker",
    author_email="ahalfaker@wikimedia.org",
    description=("A webserver for hosting scoring services."),
    license="MIT",
    entry_points = {
        'console_scripts': [
            'ores = ores.ores:main',
        ],
    },
    url="https://github.com/halfak/Objective-Revision-Evaluation-Service",
    packages=find_packages(),
    long_description=read('README.md'),
    install_requires=list(requirements("requirements.txt")),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
)
