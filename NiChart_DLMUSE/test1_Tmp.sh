#! /bin/bash

indir='../test/input'
outdir='../test/out_v5'
device='cpu'

# NiChart_DLMUSE -i $indir -o $outdir -d $device
python __main__.py -i $indir -o $outdir -d $device
