#!/opt/homebrew/opt/python@3.10/bin/python3.10

import argparse
import numpy as np
import sys
import struct
import matplotlib.pylab as plt

## Parse command line arguments & set default values
parser = argparse.ArgumentParser()
parser.add_argument('-f',   dest='infile',          help='set the input file name')
parser.add_argument('-r',   dest='nread', type=int, help='read this many spectra (default=300)',default=300) 
parser.add_argument('-s',   dest='nskip', type=int, help='skip this many spectra (default=0)', default=0) 
parser.add_argument('-src', dest='src',             help='source, e.g. U for Uranus, N for Neptune (default: U)', default='U')
parser.add_argument('-fil', dest='fil',             help='write out a SIGPROC filterbank file (default=do not)', action='store_const', const='y', default='n')
args      = parser.parse_args()
infile    = args.infile
nread     = args.nread
nskip     = args.nskip
src       = args.src
fil	  = args.fil
#print(infile)
nsweeps    = 8
nrecords   = nread//8
recordsize = 2286    # bytes
nchans     = 35      
empty      = b'  '
L = np.zeros((nsweeps*nrecords,nchans),dtype=np.uint32)
R = np.zeros((nsweeps*nrecords,nchans),dtype=np.uint32)

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
  ss = round((((s*24-hh)*60) - mm)*60)
  print("Time of day (hh:mm:ss):",hh,":",mm,":",ss)

  for sweeps in range(0,nsweeps):
    i = record*nsweeps + sweeps
    status_word = f.read(2)
    status_word = f.read(2) # just the last byte
    # Last 12 bits are used. LSB=0, up to 11
    # Of these bits 9 and 10 give the first polarisaton 
    # So that is the 10th and 11th bits
    # 0 --> R L; 1 --> L R
#    print(struct.unpack('<B',status_word)[0])
    rfirst=1
    if ((struct.unpack('<H',status_word)[0] >> 9) & 1 == 0 and (struct.unpack('<H',status_word)[0] >> 10) == 0):
#      print("BOTH ZERO")
#    print((struct.unpack('<H',status_word)[0] >> 9) & 1)  # the 10th last bit
#    print((struct.unpack('<H',status_word)[0] >> 10) & 1)  # the 11th last bit
      rfirst=1

    for j in range(0,35):
#      R[i][j] = f.read(2)
#      L[i][j] = f.read(2)
#   This worked fine up to 704 sweeps in to my test file where empty 
#   values are hit.
#   So I put in this below ugly-but-it-works check
#   Can't immediately see a nicer way to do it based on the status word
      r = f.read(4)
      l = f.read(4)
      if ( r == empty):
        r = '0'
      if ( l == empty):
        l = '0'
      if (rfirst == 0):
        R[i][j] = l
        L[i][j] = r
      else:
        R[i][j] = r
        L[i][j] = l
#      print(struct.unpack('<H',L[i][j])[0])
#      print(struct.unpack('<H',R[i][j])[0])

  if (src == "U"):
    bla = f.read(2)      # added this as 12 + 71*4*8 == 2284, not 2286.
  elif (src == "N"):
    bla = f.read(1)      # seems to be just 1 extra useless byte for Neptune data
#  Print(record)
  print(f.tell())

#from maser.data import Data
#data=Data(filepath='VG2_URN_PRA_6SEC.LBL')
#data_array=data.as_xarray()

#print(L[100])
#print(R[100])
#plt.plot((R[0]).T)
#plt.show()
#sys.exit()
plt.imshow((L**2).T, cmap='Greys',interpolation='none',origin='lower',aspect=5)
plt.show()
plt.imshow((R**2).T, cmap='Greys',interpolation='none',origin='lower',aspect=5)
plt.show()
plt.imshow((L**2+R**2).T, cmap='Greys',interpolation='none',origin='lower',aspect=5)
plt.show()

f.close()

if (fil == 'y'):
  print("Writing out SIGPROC filterbank files")
  g = open("L.fil",'wb')
  h = open("R.fil",'wb')
  g.write(L)
  h.write(R)
  g.close()
  h.close()

sys.exit()
