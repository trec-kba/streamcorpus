'''
You can run this script like this using GNU Parallel:

ls paths/x???? | ./parallel -j 32 --eta "cat {} | python filter-streamitems-cpp.py 1> {}.speed.log 2> {}.errors.log  {}" &> parallel.log & 

The streamcorpus-counter is a program like the one posted here:
  https://groups.google.com/d/msg/streamcorpus/fi8Y8yseF8o/viJjiFNVLNsJ

'''

from __future__ import division  ## get float division
import os
import sys 
import time
import shutil
import requests
from subprocess import Popen, PIPE
import streamcorpus

gpg_private='trec-kba-rsa'

gpg_dir = '/tmp/foo'
if not os.path.exists(gpg_dir):
    ## remove the gpg_dir
    #shutil.rmtree(gpg_dir, ignore_errors=True)
    os.makedirs(gpg_dir)

cmd = 'gpg --homedir %s --no-permission-warning --import %s 2> gpg_errors.log' % (gpg_dir, gpg_private)
# print cmd
gpg_child = Popen([cmd], shell=True)

start_time = time.time()
si_count = 0
chunk_count = 0
for line in sys.stdin:
    chunk_count += 1
    url = 'http://s3.amazonaws.com/aws-publicdatasets/' + line.strip()
    cmd = '(wget -O - %s | gpg --homedir %s --no-permission-warning --trust-model always --output - --decrypt - | xz --decompress | ./streamcorpus-counter) 2>> subprocess_errors.log' % (url, gpg_dir)
    child = Popen(cmd, stdout=PIPE, shell=True)
    print '%s:%s' % (line.strip(), ','.join(child.stdout.read().splitlines()))

## remove the gpg_dir
shutil.rmtree(gpg_dir, ignore_errors=True)
