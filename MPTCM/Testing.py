import MainCore
import numpy

test_sys = MainCore.OperatingSystem(   '/Users/cherudim/Desktop/DBLP/DBLPdata/1424953.txt',  # dataset path

     #'/Users/cherudim/Desktop/DBLP/DBLPdata/collaboration.txt',
    # '/Users/cherudim/Desktop/DBLP/DBLPdata/blank.txt',
     #'/Users/cherudim/Desktop/DBLP/DBLPdata/test111.txt',
    numpy.uint8, 8,  # basic datatype
    100,  # matrix size
    1,  # pyramid size

     #"single_hash"
)
