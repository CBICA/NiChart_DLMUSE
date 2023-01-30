# niCHARTPipelines


# Instructions
1) create a new conda env
```
conda create --name sMRI python=3.6.9
conda activate sMRI
```
2) Clone and install DeepMRSeg 
```
git clone  https://github.com/CBICA/DeepMRSeg.git
cd DeepMRSeg
python setup.py install
cd ..
```

2) Clone and install niCHARTPipelines
```
git clone  https://github.com/CBICA/niCHARTPipelines.git
cd niCHARTPipelines
pip install -r requirements.txt
cd ..
```

5) Run niCHARTPipelines. Example usage below
```
cd niCHARTPipelines/niCHARTPipelines
./test1_Tmp.sh

python __main__.py --pipelineType structural --inImg $t1 --DLICVmdl $mdlDLICV --DLMUSEmdl $mdlMUSE --scanID $mrid --derivedROIMappingsFile $rois --outFile $outcsv
```

