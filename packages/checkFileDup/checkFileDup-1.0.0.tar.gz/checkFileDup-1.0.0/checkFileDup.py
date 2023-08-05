#!/usr/bin/python

"""
python script that takes a single arg which is a point in a linux directory structure.  Script recursively searches for all files, runs and md5sum against all files found, and then determines duplicate files based on matching md5sum calulations.
"""
import os
import sys
import hashlib


dir = sys.argv[1]
dict = {}
md5s = []
dups = []
report = {}

#creat dictionary holding key=file, value=md5checksum for all file items in directory, recursive
for base,directory,file in os.walk(dir):
  for name in file:
    f = os.path.join(base,name)
    picture = open(f,"r")
    m = hashlib.md5()
    m.update(picture.read())
    checkSum = m.hexdigest()
    dict[f] = checkSum
    
#create list of checksums to search for dups
#old way# md5s = [v for k,v in dict.items()]
md5s = dict.values()

#find duplicate hashes, flag as dup, add to dups list
for i in md5s:
  if md5s.count(i) > 1:
    dups.append(i)

#create set of dups list to drop identical hashes
dups = set(dups) 

for i in dups: 
  for k,v in dict.items():
    if v == i:
      if not report.has_key(v):
        report[v] = [[k]]
      else:
        report[v].append([k])
      
#finally print dictionary of duplicate files
for k,v in report.items():
  print k
  for i in v:
    print i
  print
  
