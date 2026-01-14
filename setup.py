from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='pyspikex',
    version='0.6.24',
    description='Python3 Spikex.com HTTP API Connector',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kelvinxue/pyspikex",
    download_url='https://github.com/kelvinxue/pyspikex/archive/refs/tags/v0.6.24.tar.gz',
    license="MIT License",
    author="spikex",
    author_email="spikex@spikex.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="spikex api connector",
    packages=["pyspikex", "pyspikex.websocket"],
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.22.0",
        "websocket-client>=1.0.0"
    ]
)
