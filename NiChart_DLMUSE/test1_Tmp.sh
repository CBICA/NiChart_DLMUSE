#! /bin/bash

indir='/home/guraylab/GitHub/CBICA/TestData/DLICV_Test/input'
outdir='/home/guraylab/GitHub/CBICA/TestData/DLICV_Test/out_v1'

NiChart_DLMUSE -i $indir -outFile $outdir
python __main__ -i $indir -outFile $outdir
