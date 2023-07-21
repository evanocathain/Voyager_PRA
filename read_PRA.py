#!/opt/homebrew/opt/python@3.10/bin/python3.10

import argparse
import numpy as np
import sys
import struct
import matplotlib.pylab as plt

## Parse command line arguments & set default values
parser = argparse.ArgumentParser()
parser.add_argument('-f', dest='infile', help='set the input file name')
parser.add_argument('-r', dest='nread', type=int, help='read this many spectra (default=300)',default=300) 
parser.add_argument('-s', dest='nskip', type=int, help='skip this many spectra (default=0)', default=0) 
args      = parser.parse_args()
infile    = args.infile
nread     = args.nread
nskip     = args.nskip
#print(infile)
nsweeps = 8
nrecords = nread//8
recordsize = 2286    # bytes
empty    = b'  '
L = np.zeros((nsweeps*nrecords,70),dtype=np.uint16)
R = np.zeros((nsweeps*nrecords,70),dtype=np.uint16)

## https://pds-ppi.igpp.ucla.edu/ditdos/viewFile?id=pds://PPI/VG2-U-PRA-3-RDR-LOWBAND-6SEC-V1.0/DATA/VG2_URN_PRA_6SEC.LBL
f = open(infile, 'rb')
f.seek((nskip//nsweeps)*recordsize)

for record in range(0,nrecords):
#  print(record)
#  print(f.tell())
  date = f.read(6)       # first column in record is 6 bytes
  print("Date (YYDDMM): ",date.decode())
  sec = f.read(6)        # second column in record is 6 bytes
  print("Seconds since midnight:",sec.decode())
  s  = float(sec.decode())/86400.0
  hh = int(s*24)
  mm = int((s*24-hh)*60)
  ss = int((((s*24-hh)*60) - mm)*60)
  print("Time of day (hh:mm:ss):",hh,":",mm,":",ss)

  for sweeps in range(0,nsweeps):
    i = record*nsweeps + sweeps
    status_word = f.read(3)
    status_word = f.read(1) # just the last byte
    # Last 12 bits are used. Of these the 9th and 10th give the first polarisaton 
    # 0 --> R L; 1 --> L R
#    print((struct.unpack('<B',status_word)[0] >> 3) & 1)  # the 9th bit
#    print((struct.unpack('<B',status_word)[0] >> 2) & 1)  # the 10th bit

    for j in range(0,70):
#      L[i][j] = f.read(2)
#      R[i][j] = f.read(2)
#   This worked fine up to 704 sweeps in to my test file where empty 
#   values are hit.
#   So I put in this below ugly-but-it-works check
#   Can't immediately see a nicer way to do it based on the status word
      l = f.read(2)
      r = f.read(2)
      if ( l == empty):
        l = '0'
      if ( r == empty):
        r = '0'
      L[i][j] = l
      R[i][j] = r
#      print(struct.unpack('<H',L[i][j])[0])
#      print(struct.unpack('<H',R[i][j])[0])

  bla = f.read(2)      # added this as 12 + 71*4*8 == 2284, not 2286.
#  print(record)
#  print(f.tell())

#from maser.data import Data
#data=Data(filepath='VG2_URN_PRA_6SEC.LBL')
#data_array=data.as_xarray()

plt.imshow((L).T, cmap='Greys',interpolation='none',origin='lower',aspect=5)
plt.show()
plt.imshow((R).T, cmap='Greys',interpolation='none',origin='lower',aspect=5)
plt.show()
plt.imshow((L**2+R**2).T, cmap='Greys',interpolation='none',origin='lower',aspect=5)
plt.show()

sys.exit()
