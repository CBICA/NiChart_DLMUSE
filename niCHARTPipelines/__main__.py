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
    parser.add_argument('--inImg', type=str, help='Input T1 image file path.', default=None, required=False)
    parser.add_argument('--DLICVmdl', type=str, help='DLICV model path.', default=None, required=False)
    parser.add_argument('--DLMUSEmdl', type=str, help='DLMUSE Model path.', default=None, required=False)
    parser.add_argument('--pipelineType', type=str, help='Specify type of pipeline[structural, dti, fmri].', default=None, required=True)
    parser.add_argument('--outImg', type=str, help='Output file name with extension.', default=None, required=False)
    
    args = parser.parse_args(sys.argv[1:])

    inImg = args.inImg
    DLICVmdl = args.DLICVmdl
    DLMUSEmdl = args.DLMUSEmdl
    pipelineType = args.pipelineType
    outImg = args.outImg

    if(pipelineType == "structural"):
        # if((DLICV_model_file == None) or (DLMUSE_model_file == None)):
        #print("Please provide '--DLICV_model_file','--DLMUSE_model_file' to run the pipeline.")
        #exit()
        Structural.run_structural_pipeline()
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
