# cython: profile=True
# Time-stamp: <2012-09-14 02:04:34 Tao Liu>

"""Module Description

Copyright (c) 2012 Hanfei Sun <ad9075@gmail.com>, Tao Liu <taoliu@jimmy.harvard.edu>

This code is free software; you can redistribute it and/or modify it
under the terms of the Artistic License (see the file COPYING included
with the distribution).

@status:  experimental
@version: $Revision$
@author:  Hanfei Sun, Tao Liu
@contact: taoliu@jimmy.harvard.edu
"""

import os
import sys
import argparse
from math import sqrt
from collections import Counter
from itertools import tee, ifilterfalse, ifilter

import pysam

sorted_prefix = lambda path: path + ".sorted"
sorted_path = lambda path: sorted_prefix(path) + ".bam"

def make_index(in_bam, max_mem = 500000000):
    bai_path = lambda path: sorted_path(path) + ".bai"

    
    if not os.path.exists(sorted_path(in_bam)):
        pysam.sort("-m",str(max_mem),in_bam, sorted_prefix(in_bam))
    print "sorted"
        
    if not os.path.exists(bai_path(in_bam)):
        pysam.index(sorted_path(in_bam))
    print "indexed"
    return bai_path(in_bam)

def find_summit(bed_file, sam_file, window_size, output_file):
    def count_by_strand(ialign):
        pred = lambda x:x.is_reverse
        watson_5_end = lambda x:x.pos
        crick_5_end = lambda x:x.aend
        ialign1, ialign2 = tee(ialign)

        return (Counter(map(watson_5_end,
                            ifilterfalse(pred, ialign1))),
                Counter(map(crick_5_end,
                            ifilter(pred, ialign2))))
    
    left_sum = lambda strand, pos, width = window_size: sum([strand[x] for x in strand if x <= pos and x >= pos - width])
    right_sum = lambda strand, pos, width = window_size: sum([strand[x] for x in strand if x >= pos and x <= pos + width])
    left_forward = lambda strand, pos: strand.get(pos,0) - strand.get(pos-window_size, 0)
    right_forward = lambda strand, pos: strand.get(pos + window_size, 0) - strand.get(pos, 0)
    samfile = pysam.Samfile(sam_file, "rb" )

    cnt = 0
    with open(bed_file) as bfile, open(output_file,"w") as ofile:
        for i in bfile:
            i = i.split("\t")
            chrom = i[0]
            peak_start = int(i[1])
            peak_end = int(i[2])
            
            watson, crick = count_by_strand(samfile.fetch(chrom, peak_start-window_size, peak_end+window_size))
            watson_left = left_sum(watson, peak_start)
            crick_left = left_sum(crick, peak_start)
            watson_right = right_sum(watson, peak_start)
            crick_right = right_sum(crick, peak_start)

            wtd_list = []
            for j in range(peak_start, peak_end+1):
                wtd_list.append(2 * sqrt(watson_left * crick_right) - watson_right - crick_left)
                watson_left += left_forward(watson, j)
                watson_right += right_forward(watson, j)
                crick_left += left_forward(crick, j)
                crick_right += right_forward(crick,j)

            wtd_max_val = max(wtd_list)
            wtd_max_pos = wtd_list.index(wtd_max_val) + peak_start
            cnt += 1

            ofile.write("{}\t{}\t{}\tSPP_summit_{}\t{:.2f}\n".format(chrom,
                                                                     wtd_max_pos,
                                                                     wtd_max_pos+1,
                                                                     cnt,
                                                                     wtd_max_val,))
    samfile.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SPP method')
    parser.add_argument('-a','--bam', help='BAM alignment file', required=True)
    parser.add_argument('-b','--bed', help='BED peak file', required=True)
    parser.add_argument('-o','--output', help='output BED summit file', required=True)
    parser.add_argument('-w','--window-size', help='window size on both side of the summit (default: 200bp)', type=int, default=200)
    parser.add_argument('--sort', help='whether to use samtools to sort the bam file', action="store_true", default=False)
    
    args = parser.parse_args()
    if args.sort:
        make_index(args.bam)
        find_summit(args.bed, sorted_path(args.bam), args.window_size, args.output)
    else:
        if os.path.exists(args.bam+".bai"):
            find_summit(args.bed, args.bam, args.window_size, args.output)
        else:
            print "bai file doesn't exist, please make sure you have already make the index"



    
    
