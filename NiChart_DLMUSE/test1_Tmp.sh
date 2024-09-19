#! /bin/bash

indir='./test/input'
outdir='./test/out_v1'

NiChart_DLMUSE -i $indir -o $outdir
python __main__ -i $indir -outFile $outdir
