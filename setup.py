import os
import platform
import re
import sys

from setuptools import find_packages, setup

about_path = os.path.join(os.path.dirname(__file__), "ores/about.py")
exec(compile(open(about_path).read(), about_path, "exec"))

if sys.version_info <= (3, 0):
    print("ORES needs Python 3 to run properly. Your version is " + platform.python_version())
    sys.exit(1)


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
    python_requires=">=3",
    name=__name__,  # noqa
    version=__version__,  # noqa
    author=__author__,  # noqa
    author_email=__author_email__,  # noqa
    description=__description__,  # noqa
    url=__url__,  # noqa
    license=__license__,  # noqa
    entry_points={
        'console_scripts': [
            'ores = ores.ores:main',
        ],
    },
    packages=find_packages(),
    include_package_data=True,
    long_description=read('README.md'),
    install_requires=list(requirements("requirements.txt")),
    extras_require={
        # Install ores[redis] if your deployment will use the Redis scoring
        # cache and Celery backend.
        "redis": [
            "pylru",
            "redis",
        ],
    },
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
