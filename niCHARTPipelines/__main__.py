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
    parser = argparse.ArgumentParser(description='niCHART Data Pre-Preprocessing Pipelines')
    parser.add_argument('--input_image_file', type=str, help='Data file containing data frame.', default=None, required=False)
    parser.add_argument('--DLICV_model_file', type=str, help='Harmonization model file.', default=None, required=False)
    parser.add_argument('--DLMUSE_model_file', type=str, help='Model file for SPARE-scores.', default=None, required=False)
    parser.add_argument('--pipeline_type', type=str, help='Specify type of pipeline[structural, dti, fmri].', default=None, required=True)
    parser.add_argument('--output_file_name', type=str, help='Name of the output file with extension.', default=None, required=False)
    
    args = parser.parse_args(sys.argv[1:])

    input_image_file = args.input_image_file
    DLICV_model_file = args.DLICV_model_file
    DLMUSE_model_file = args.DLMUSE_model_file
    pipeline_type = args.pipeline_type
    output_file = args.output_file_name

    if(pipeline_type == "structural"):
        # if((DLICV_model_file == None) or (DLMUSE_model_file == None)):
        #print("Please provide '--DLICV_model_file','--DLMUSE_model_file' to run the pipeline.")
        #exit()
        Structural.run_structural_pipeline()
    elif(pipeline_type == "fmri"):
        print("Coming soon.")
        exit()
    elif(pipeline_type == "dti"):
        print("Coming soon.")
        exit()
    else:
        print("Only [structural, dti and fmri] pipelines are supported.")
        exit()



if __name__ == '__main__':
    main()
