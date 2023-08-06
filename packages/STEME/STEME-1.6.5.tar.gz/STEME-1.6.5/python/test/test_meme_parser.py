#
# Copyright John Reid 2010, 2012
#

"""
Test biopython MEME parser.
"""

import cStringIO

meme_output = cStringIO.StringIO("""
********************************************************************************
MEME - Motif discovery tool
********************************************************************************
MEME version 4.3.0 (Release date: Sat Sep 26 01:51:56 PDT 2009)

For further information on how to interpret these results or to get
a copy of the MEME software please access http://meme.nbcr.net.

This file may be used as input to the MAST algorithm for searching
sequence databases for matches to groups of motifs.  MAST is available
for interactive use and downloading at http://meme.nbcr.net.
********************************************************************************


********************************************************************************
REFERENCE
********************************************************************************
If you use this program in your research, please cite:

Timothy L. Bailey and Charles Elkan,
"Fitting a mixture model by expectation maximization to discover
motifs in biopolymers", Proceedings of the Second International
Conference on Intelligent Systems for Molecular Biology, pp. 28-36,
AAAI Press, Menlo Park, California, 1994.
********************************************************************************


********************************************************************************
TRAINING SET
********************************************************************************
DATAFILE= /home/john/Data/Tompa-data-set/Real/hm22r.fasta
ALPHABET= ACGT
Sequence name            Weight Length  Sequence name            Weight Length  
-------------            ------ ------  -------------            ------ ------  
seq_0                    1.0000    500  seq_1                    1.0000    500  
seq_2                    1.0000    500  seq_3                    1.0000    500  
seq_4                    1.0000    500  seq_5                    1.0000    500  
********************************************************************************

********************************************************************************
COMMAND LINE SUMMARY
********************************************************************************
This information can also be useful in the event you wish to report a
problem with the MEME software.

command: meme /home/john/Data/Tompa-data-set/Real/hm22r.fasta -maxsize 1000000 -oc output/run_dataset/Tompa/hm22r/Real -dna -mod anr -revcomp -print_starts -maxiter 1000 -minw 8 -maxw 20 -minsites 2 -nmotifs 1 

model:  mod=           anr    nmotifs=         1    evt=           inf
object function=  E-value of product of p-values
width:  minw=            8    maxw=           20    minic=        0.00
width:  wg=             11    ws=              1    endgaps=       yes
nsites: minsites=        2    maxsites=       30    wnsites=       0.8
theta:  prob=            1    spmap=         uni    spfuzz=        0.5
global: substring=     yes    branching=      no    wbranch=        no
em:     prior=   dirichlet    b=            0.01    maxiter=      1000
        distance=    1e-05
data:   n=            3000    N=               6
strands: + -
sample: seed=            0    seqfrac=         1
Letter frequencies in dataset:
A 0.195 C 0.305 G 0.305 T 0.195 
Background letter frequencies (from dataset with add-one prior applied):
A 0.195 C 0.305 G 0.305 T 0.195 
********************************************************************************


********************************************************************************
MOTIF  1    width =   11   sites =  15   llr = 159   E-value = 9.8e-006
********************************************************************************
--------------------------------------------------------------------------------
    Motif 1 Description
--------------------------------------------------------------------------------
Simplified        A  71:439:9:91
pos.-specific     C  ::::::8::::
probability       G  18a37:2:a19
matrix            T  31:3:1:1:::

         bits    2.4            
                 2.1      *     
                 1.9      * * * 
                 1.6   *  * *** 
Relative         1.4   *  * ****
Entropy          1.2 * *  * ****
(15.3 bits)      0.9 *** *******
                 0.7 ***********
                 0.5 ***********
                 0.2 ***********
                 0.0 -----------

Multilevel           AGGAGACAGAG
consensus            T  TA G    
sequence                G       
                                
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
    Motif 1 sites sorted by position p-value
--------------------------------------------------------------------------------
Sequence name            Strand  Start   P-value               Site  
-------------            ------  ----- ---------            -----------
seq_3                        -    213  4.54e-07 GGCCTTTGGA AGGTGACAGAG GCGCGGCCAC
seq_1                        -    146  4.54e-07 CCCAACAGGA AGGTGACAGAG GTGGCTCTGG
seq_0                        +    490  4.54e-07 AAAACAGCAG AGGTGACAGAG           
seq_0                        -     83  4.54e-07 CCCAGCAGGA AGGTGACAGAG GTGGCTCTGG
seq_0                        +    388  5.99e-07 ATGAGAGGAG AGGAAACAGAG CTTCCTGGAC
seq_1                        +    422  1.10e-06 ATGAGAGGGG AGGGGACAGAG GACACCTGAA
seq_1                        +     79  1.33e-06 TTGGTGGTAC TGGAGACAGAG GGCTGGTCCC
seq_0                        +    281  3.17e-06 CCTCCCCTGA TGGGGACAGAG GTCTCATCAG
seq_0                        +     16  5.72e-06 CTGGTGACAC TAGAGACAGAG GGCTGGTCCC
seq_1                        -    228  1.18e-05 TTATTTTCCT TTGTGACAGAG AAACCCAGCA
seq_4                        +    156  2.07e-05 TCAAGTCCCA AGGGGACAGGG AGCAGAAGGG
seq_0                        +    348  2.47e-05 GTAGACAGAA AGGAAAGAGAA AGTAAGGACA
seq_0                        +    374  3.14e-05 GGACAAAGGT AGGAATGAGAG GAGAGGAAAC
seq_5                        -     22  4.53e-05 CTCTTGTGTA GGGAAACTGAG CACGGGGAAC
seq_3                        +    486  5.02e-05 CGCCAATGGG AAGGGAGTGAG TGCC      
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
    Motif 1 block diagrams
--------------------------------------------------------------------------------
SEQUENCE NAME            POSITION P-VALUE  MOTIF DIAGRAM
-------------            ----------------  -------------
seq_3                               5e-05  212_[-1]_262_[+1]_4
seq_1                             1.2e-05  78_[+1]_56_[-1]_71_[-1]_183_[+1]_68
seq_0                             3.2e-06  15_[+1]_56_[-1]_187_[+1]_56_[+1]_
                                           15_[+1]_3_[+1]_91_[+1]
seq_4                             2.1e-05  155_[+1]_334
seq_5                             4.5e-05  21_[-1]_468
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
    Motif 1 in BLOCKS format
--------------------------------------------------------------------------------
BL   MOTIF 1 width=11 seqs=15
seq_3                    (  213) AGGTGACAGAG  1 
seq_1                    (  146) AGGTGACAGAG  1 
seq_0                    (  490) AGGTGACAGAG  1 
seq_0                    (   83) AGGTGACAGAG  1 
seq_0                    (  388) AGGAAACAGAG  1 
seq_1                    (  422) AGGGGACAGAG  1 
seq_1                    (   79) TGGAGACAGAG  1 
seq_0                    (  281) TGGGGACAGAG  1 
seq_0                    (   16) TAGAGACAGAG  1 
seq_1                    (  228) TTGTGACAGAG  1 
seq_4                    (  156) AGGGGACAGGG  1 
seq_0                    (  348) AGGAAAGAGAA  1 
seq_0                    (  374) AGGAATGAGAG  1 
seq_5                    (   22) GGGAAACTGAG  1 
seq_3                    (  486) AAGGGAGTGAG  1 
//

--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
    Motif 1 position-specific scoring matrix
--------------------------------------------------------------------------------
log-odds matrix: alength= 4 w= 11 n= 2940 bayes= 6.7534 E= 9.8e-006 
   177  -1055   -219     45 
   -55  -1055    139   -155 
 -1055  -1055    171  -1055 
   103  -1055    -19     77 
    45  -1055    127  -1055 
   226  -1055  -1055   -155 
 -1055    139    -61  -1055 
   215  -1055  -1055    -55 
 -1055  -1055    171  -1055 
   226  -1055   -219  -1055 
  -155  -1055    161  -1055 
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
    Motif 1 position-specific probability matrix
--------------------------------------------------------------------------------
letter-probability matrix: alength= 4 w= 11 nsites= 15 E= 9.8e-006 
 0.666667  0.000000  0.066667  0.266667 
 0.133333  0.000000  0.800000  0.066667 
 0.000000  0.000000  1.000000  0.000000 
 0.400000  0.000000  0.266667  0.333333 
 0.266667  0.000000  0.733333  0.000000 
 0.933333  0.000000  0.000000  0.066667 
 0.000000  0.800000  0.200000  0.000000 
 0.866667  0.000000  0.000000  0.133333 
 0.000000  0.000000  1.000000  0.000000 
 0.933333  0.000000  0.066667  0.000000 
 0.066667  0.000000  0.933333  0.000000 
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
    Motif 1 regular expression
--------------------------------------------------------------------------------
[AT]GG[ATG][GA]A[CG]AGAG
--------------------------------------------------------------------------------




Time  3.78 secs.

********************************************************************************


********************************************************************************
SUMMARY OF MOTIFS
********************************************************************************

--------------------------------------------------------------------------------
    Combined block diagrams: non-overlapping sites with p-value < 0.0001
--------------------------------------------------------------------------------
SEQUENCE NAME            COMBINED P-VALUE  MOTIF DIAGRAM
-------------            ----------------  -------------
seq_0                            4.45e-04  15_[+1(5.72e-06)]_56_[-1(4.54e-07)]_187_[+1(3.17e-06)]_56_[+1(2.47e-05)]_15_[+1(3.14e-05)]_3_[+1(5.99e-07)]_91_[+1(4.54e-07)]
seq_1                            4.45e-04  78_[+1(1.33e-06)]_56_[-1(4.54e-07)]_71_[-1(1.18e-05)]_183_[+1(1.10e-06)]_68
seq_2                            2.03e-01  500
seq_3                            4.45e-04  212_[-1(4.54e-07)]_262_[+1(5.02e-05)]_4
seq_4                            2.01e-02  155_[+1(2.07e-05)]_334
seq_5                            4.34e-02  21_[-1(4.53e-05)]_468
--------------------------------------------------------------------------------

********************************************************************************


********************************************************************************
Stopped because nmotifs = 1 reached.
********************************************************************************

CPU: john-dell

********************************************************************************
""")


from Bio import Motif

print '#Sequence, start, length, site'
for motif in Motif.parse(meme_output, "MEME"):
    print 'Motif: E-value: %f' % motif.evalue
    for instance in motif.instances:
        print "%10s, %5d, %5d, %s" % (
            instance.sequence_name,
            instance.start,
            instance.length,
            str(instance),
        )
        assert instance.length == motif.length, '%d != %d' % (instance.length, motif.length)
