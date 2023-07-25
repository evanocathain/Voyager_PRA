#!/opt/homebrew/opt/python@3.10/bin/python3.10

import argparse
import numpy as np
import sys
import struct

## Parse command line arguments & set default values
parser = argparse.ArgumentParser()
parser.add_argument('-f',    dest='infile',          help='set the input file name')
parser.add_argument('-fil',  dest='fil',             help='write out a SIGPROC filterbank file (default=do not)', action='store_const', const='y', default='n')
parser.add_argument('-plot', dest='plot',            help='plot to screen (default=do not)', action='store_const', const='y', default='n')
parser.add_argument('-r',    dest='nread', type=int, help='read this many spectra (default=300)',default=300) 
parser.add_argument('-s',    dest='nskip', type=int, help='skip this many spectra (default=0)', default=0) 
parser.add_argument('-src',  dest='src',             help='source, e.g. U for Uranus, N for Neptune (default: U)', default='U')
parser.add_argument('-v',    dest='v',               help='print verbose output to screen (default=not verbose)', action='store_const', const='y', default='n')
args      = parser.parse_args()
infile    = args.infile
fil       = args.fil
plot	  = args.plot
nread     = args.nread
nskip     = args.nskip
src       = args.src
v         = args.v
nsweeps    = 8
nrecords   = nread//nsweeps
recordsize = 2286    # bytes
nchans     = 35      
L = np.zeros((nsweeps*nrecords,nchans),dtype=np.uint32)
R = np.zeros((nsweeps*nrecords,nchans),dtype=np.uint32)

## https://pds-ppi.igpp.ucla.edu/ditdos/viewFile?id=pds://PPI/VG2-U-PRA-3-RDR-LOWBAND-6SEC-V1.0/DATA/VG2_URN_PRA_6SEC.LBL
f = open(infile, 'rb')
f.seek((nskip//nsweeps)*recordsize)

rfirst=True
for record in range(0,nrecords):
  date = f.read(6)       # first column in record is 6 bytes
  sec  = f.read(6)       # second column in record is 6 byte
  if ( v == 'y'):
    print("Date (YYDDMM): ",date.decode())
    print("Seconds since midnight:",sec.decode())
    s  = float(sec.decode())/86400.0
    hh = int(s*24)
    mm = int((s*24-hh)*60)
    ss = round((((s*24-hh)*60) - mm)*60)
    print("Time of day (hh:mm:ss):",hh,":",mm,":",ss)

  for sweeps in range(0,nsweeps):
    i = record*nsweeps + sweeps
    status_word = f.read(4)
    for j in range(0,35):
      if (rfirst):
        R[i][j] = f.read(4)
        L[i][j] = f.read(4)
      else:
        L[i][j] = f.read(4)
        R[i][j] = f.read(4)
    rfirst = not rfirst  # next sweep is opposite way around

  if (src == "U"):
    bla = f.read(2)      # added this as 12 + 71*4*8 == 2284, not 2286.
  elif (src == "N"):
    bla = f.read(1)      # seems to be just 1 extra useless byte for Neptune data

f.close()

if (plot == 'y'):
  # Plot things
  import matplotlib.pylab as plt
  plt.imshow((L).T, cmap='Greys',interpolation='none',origin='lower',aspect=max(5,5*int(nread/300)))
  plt.show()
  plt.imshow((R).T, cmap='Greys',interpolation='none',origin='lower',aspect=max(5,5*int(nread/300)))
  plt.show()

if (fil == 'y'):
  print("Writing out SIGPROC filterbank files")
  g = open("L.fil",'wb')
  h = open("R.fil",'wb')
  g.write(L)
  h.write(R)
  g.close()
  h.close()

sys.exit()
