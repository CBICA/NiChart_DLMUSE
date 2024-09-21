from pathlib import Path

import setuptools
from setuptools import setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="NiChart_DLMUSE",
    version="1.0.0",
    description="Run NiChart_DLMUSE on your data(currently only structural pipeline is supported).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ashish Singh, Guray Erus, George Aidinis",
    author_email="software@cbica.upenn.edu",
    maintainer="Guray Erus, Baik, Kyunglok, Spiros Maggioros",
    license="MIT",
    url="https://github.com/CBICA/NiChart_DLMUSE",
    install_requires=[
        "DLICV",
        "DLMUSE",
        "scipy",
        "pathlib",
    ],
    entry_points={"console_scripts": ["NiChart_DLMUSE = NiChart_DLMUSE.__main__:main"]},
    classifiers=[
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering",
        "Operating System :: Unix",
    ],
    packages=setuptools.find_packages(),
    include_package_data=True,
)
