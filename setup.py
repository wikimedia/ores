import os

from setuptools import find_packages, setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def requirements(fname):
    return [line.strip()
            for line in open(os.path.join(os.path.dirname(__file__), fname))]

setup(
    name="ores",
    version="0.0.1", # Update in ores/__init__.py too.
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
    install_requires=requirements("requirements.txt"),
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
