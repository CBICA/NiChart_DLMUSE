# This Python file uses the following encoding: utf-8
"""
contact: software@cbica.upenn.edu
Copyright (c) 2018 University of Pennsylvania. All rights reserved.
Use of this source code is governed by license located in license file: https://github.com/CBICA/NiBAx/blob/main/LICENSE
"""

import argparse
import os, sys
import Structural

def main():
    parser = argparse.ArgumentParser(description='niCHART Data Preprocessing Pipelines')
    parser.add_argument('--inImg', type=str, help='Input T1 image file path.', default=None, required=True)
    parser.add_argument('--DLICVmdl', type=str, help='DLICV model path.', default=None, required=True)
    parser.add_argument('--DLMUSEmdl', type=str, help='DLMUSE Model path.', default=None, required=True)
    parser.add_argument('--pipelineType', type=str, help='Specify type of pipeline[structural, dti, fmri].', default=None, required=True)
    parser.add_argument('--outFile', type=str, help='Output file name with extension.', default=None, required=True)
    parser.add_argument('--scanID', type=str, help='scan id.', default=None, required=True)
    parser.add_argument('--derivedROIMappingsFile', type=str, help='derived MUSE ROI mappings file.', default=None, required=True)
    parser.add_argument('--MuseROIMappingsFile', type=str, help='MUSE ROI mappings file.', default=None, required=True)
    
    args = parser.parse_args(sys.argv[1:])

    inImg = args.inImg
    DLICVmdl = args.DLICVmdl
    DLMUSEmdl = args.DLMUSEmdl
    pipelineType = args.pipelineType
    outFile = args.outFile
    scanID = args.scanID
    roiMappingsFile = args.derivedROIMappingsFile
    MuseroiMappingsFile = args.MuseROIMappingsFile

    if(pipelineType == "structural"):
        Structural.run_structural_pipeline(inImg,DLICVmdl,DLMUSEmdl,outFile,MuseroiMappingsFile,scanID,roiMappingsFile)
    elif(pipelineType == "fmri"):
        print("Coming soon.")
        exit()
    elif(pipelineType == "dti"):
        print("Coming soon.")
        exit()
    else:
        print("Only [structural, dti and fmri] pipelines are supported.")
        exit()


if __name__ == '__main__':
    main()
