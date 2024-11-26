from pathlib import Path

from setuptools import find_packages, setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="NiChart_DLMUSE",
    version="1.0.8",
    description="Run NiChart_DLMUSE on your data (currently only structural pipeline is supported).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Guray Erus, Wu Di, Kyunglok Baik, George Aidinis",
    author_email="software@cbica.upenn.edu",
    maintainer="Guray Erus, Kyunglok Baik, Spiros Maggioros, Alexander Getka",
    license="By installing/using DLMUSE, the user agrees to the following license: See https://www.med.upenn.edu/cbica/software-agreement-non-commercial.html",
    url="https://github.com/CBICA/NiChart_DLMUSE",
    python_requires=">=3.9",
    install_requires=[
        "torch<=2.2.1",
        "DLICV",
        "DLMUSE",
        "huggingface_hub",
        "scipy",
        "nibabel",
        "argparse",
        "pathlib",
    ],
    entry_points={"console_scripts": ["NiChart_DLMUSE = NiChart_DLMUSE.__main__:main"]},
    classifiers=[
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering",
        "Operating System :: Unix",
    ],
    packages=find_packages(exclude=[".github"]),
    include_package_data=True,
    keywords=[
        "deep learning",
        "image segmentation",
        "semantic segmentation",
        "medical image analysis",
        "medical image segmentation",
        "nnU-Net",
        "nnunet",
    ],
    package_data={
        "NiChart_DLMUSE": ["**/*.csv", "**/*.json"],
    },
)
