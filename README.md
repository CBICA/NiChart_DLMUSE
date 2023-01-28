# niCHARTPipelines


# Instructions
1) create a new conda env
```
conda create --name sMRI python=3.6.9
conda activate sMRI
```
2) Clone niCHARTPipelines github repository
```
git clone  https://github.com/CBICA/niCHARTPipelines.git
cd niCHARTPipelines
```

3) Install dependencies
```
pip install -r requirements.txt
```
4) Clone and install DeepMRSeg 
```
git clone  https://github.com/CBICA/DeepMRSeg.git
cd DeepMRSeg
python setup.py install #install DeepMRSeg and its dependencies
```

5) Run niCHARTPipelines. Example usage below-
```
python __main__.py --pipelineType structural --inImg /nichart/data/F1/2.16.840.1.114362.1.12066432.24920037488.604832115.605.168.nii.gz --DLICVmdl /nichart/models/DLICV --DLMUSEmdl /nichart/models/MUSE --scanID AABB --derivedROIMappingsFile /nichart/csv/MUSE_DerivedROIs_Mappings.csv --outFile /nichart/data/F1/muse_rois.csv
```

