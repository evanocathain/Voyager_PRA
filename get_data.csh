#!/bin/csh

#
# This simple script will download the Voyager 1/2 PRA 
# data that are available online if it doesn't fine them
# in the current directories
#
# NB. June 2023 status: Noticed that a lot of VERY important 
#     data are missing. In particular VG2 HIGHBAND data
#     for the Uranus and Neptune fly-bys
#     Aug 2023 status: these have not yet been recovered 
#     despite many efforts from many folks.  
#

set URL = "https://pds-ppi.igpp.ucla.edu/ditdos/download?id=pds://PPI"

if (! -e `which curl`) then
  echo "Could not find curl. Exiting."
  goto death
endif

if (! -e Data) mkdir Data
cd Data

# Get Voyager 1 data
if (! -e VG1 ) mkdir VG1
cd VG1
foreach file ( `cat ../../PRA_data_list_VG1` )
  if (! -d $file ) then
    echo "Downloading "$file
    echo "$URL"/$file
    curl "$URL"/$file -o $file".zip"
    mkdir $file; mv $file".zip" $file"/"; cd $file; 
    unzip $file".zip"; rm $file".zip"; cd ..
  endif
end
cd ..

# Get Voyager 2 data
if (! -e VG2 ) mkdir VG2
cd VG2
foreach file ( `cat ../../PRA_data_list_VG2` )
  if (! -d $file ) then
    echo "Downloading "$file
    echo "$URL"/$file
    curl "$URL"/$file -o $file".zip"
    mkdir $file; mv $file".zip" $file"/"; cd $file; 
    unzip $file".zip"; rm $file".zip"; cd ..
  endif
end
cd ..

cd ..

death:
exit
