from celery.task import task
#from celery.task.sets import subtask
from subprocess import Popen, PIPE
from crackchars import getCharset

import tempfile
import os

import jconfig
config = jconfig.getConfig()

#  charset.txt must be in the CWD or rcracki_mt fails
#  ... so we just generate one ...
def checkCwd():
    os.chdir('/tmp')
    if not os.path.exists('/tmp/charset.txt'):
        f = open('/tmp/charset.txt', 'w')
        f.write(getCharset())
        f.close()    

@task
def rcrack(hashtype, hashval):

    # create tempfile, close file handle
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()

    checkCwd()

    args = [
        'rcracki_mt', 
        '-h', hashval,
        '-o', tmp.name,
        '-t', config.get('tune','threads_per_proc'),
        '/mnt/lmtables/'+hashtype,
    ]
    
    p = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    ( out, err ) = p.communicate('')    

    # if the hash is there, add it to the db
    f = open(tmp.name, 'r')
    for line in f.readlines():
        # hash:clear:???
        words = line.split(':')
        return (hashtype, hashval, words[1])
    f.close()
    # maybe delete file here?

@task
def hashcat(hashtype, hashval):

    # create tempfile, close file handle
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()

    checkCwd()

    args = [
        '/opt/oclHashcat-lite-0.09/cudaHashcat-lite64.bin', 
        '--quiet',
        '-m', hashtype,
        '--outfile-format=2', # plaintext-only
        '--outfile='+tmp.name,
        hashval,
    ]
    
    p = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    ( out, err ) = p.communicate('')    

    # if the hash is there, add it to the db
    f = open(tmp.name, 'r')
    for line in f.readlines():      
        words = line.strip()
        if len(words) > 0:
            return (hashtype, hashval, words)
    f.close()
    # maybe delete file here?

    
