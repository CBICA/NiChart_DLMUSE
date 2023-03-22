from setuptools import setup, find_packages
import setuptools
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(name='niCHARTPipelines',
      version='0.1',
      description='Run niCHARTPipelines on your data(currently only structural pipeline is supported).',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Ashish Singh',
      author_email='software@cbica.upenn.edu',
      license='MIT',
      url="https://github.com/CBICA/niCHARTPipelines",
	  install_requires=[
		'setuptools',
    'DeepMRSeg @ git+https://github.com/CBICA/DeepMRSeg.git@main',
		'nipype',
		'SimpleITK',
		'scipy==1.5.4',
		'matplotlib==3.3.3',
		'dill==0.3.4',
		'h5py==2.10.0',
		'hyperopt==0.2.5',
		'keras==2.6.0',
		'numpy==1.18.5',
		'protobuf==3.17.3',
		'pymongo==3.12.0',
		'scikit-learn==0.24.2',
		'nibabel==3.2.1',
		'resource==0.2.1',
		'networkx==2.5.1',
		'pandas==1.2.5',
		'pathlib'
    ],
    entry_points={
        'console_scripts': [
            'niCHARTPipelines = niCHARTPipelines.__main__:main'
        ]        
    },    
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        'Operating System :: Unix',
    ],
    packages=setuptools.find_packages(),
    include_package_data=True,	
      )