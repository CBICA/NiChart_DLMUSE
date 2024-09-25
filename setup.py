from pathlib import Path

import setuptools
from setuptools import setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

with open('requirements.txt') as f:
    required = f.read().splitlines()


setup(
    name="NiChart_DLMUSE",
    version="1.0.1",
    description="Run NiChart_DLMUSE on your data (currently only structural pipeline is supported).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Guray Erus, Wu Di, Kyunglok Baik, George Aidinis",
    author_email="software@cbica.upenn.edu",
    maintainer="Guray Erus, Kyunglok Baik, Spiros Maggioros, Alexander Getka",
    license="MIT",
    url="https://github.com/CBICA/NiChart_DLMUSE",
    install_requires=required,
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
