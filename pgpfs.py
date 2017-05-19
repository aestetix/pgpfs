#!bin/python
""" pgpfs is a tool to turn your friendly pgp keyserver into a redundant
persistant filesystem."""

import os
import sys
import re
import base64
from hashlib import sha256
import gnupg

os.system('rm -rf gpg')
GPG = gnupg.GPG(gnupghome='gpg')
KEYSERVER = 'pgp.mit.edu'

# trial and error lead to this number
SPLIT_LENGTH = 986

# store file

def read_file_into_list(source_file):
    """ reads file into list"""
    with open(source_file, 'r') as source:
        data = base64.b64encode(source.read())
        return [data[i:i+SPLIT_LENGTH] for i in range(0, len(data), SPLIT_LENGTH)]

def create_comment(data):
    """ takes data bit and turns it into a key comment"""
    checksum = sha256(data).hexdigest()
    comment = checksum + ' ' + data
    return comment

def create_key(name):
    """ creates gpg key out of given data"""
    input_data = GPG.gen_key_input(
        key_type='RSA',
        key_length='1024',
        name_real='PGP File System',
        name_comment=create_comment(name),
        name_email='placeholder@email.address'
    )
    return GPG.gen_key(input_data)

def send_key(key_id):
    """ uploads given key to keyserver"""
    key_id = str(key_id)
    GPG.send_keys(KEYSERVER, key_id)
    if key_id == GPG.search_keys(key_id, KEYSERVER)[0]['keyid']:
        return key_id
    else:
        error = 'Error uploading key ', key_id
        return error

def store_file(filename1, filename2):
    """ overall function to upload file to keyserver"""
    print 'Splitting ', filename1, ' into encoded comments for keys'
    file_list = read_file_into_list(filename1)
    output_file = open(filename2, 'w')
    counter_length = len(file_list)
    counter = 0
    for chunk in file_list:
        print 'Creating key ', counter, ' of ', counter_length
        counter = counter + 1
        key_id = create_key(chunk)
        output_file.write(send_key(key_id)+'\n')
        print '--> key has been created and uploaded'
    print 'File has been successfully uploaded to ', KEYSERVER

# fetch file

def get_key_comment(key_id):
    """ returns comment section of a given key"""
    return GPG.search_keys(key_id, KEYSERVER)[0]['uids']

def parse_key(key_id):
    """" parses file bit out of key comment"""
    comment = get_key_comment(key_id)[0]
    regex = re.compile(".*?\\((.*?)\\)")
    comment_bits = re.findall(regex, comment)[0].split(' ')
    if comment_bits[0] == sha256(comment_bits[1]).hexdigest():
        return comment_bits[1]

def fetch_file(index_file, filename):
    """ overall function to fetch component file parts from keyserver"""
    with open(index_file, 'r') as index, open(filename, 'w+') as download:
        print 'Fetching keys from ', KEYSERVER, ' to create ', filename
        fetched_file = ''
        index_length = len(index.readlines())
        index.seek(0) # because python is stupid
        counter = 0
        for key in index.readlines():
            print 'Fetching key ', counter, ' of ', index_length
            counter = counter + 1
            fetched_file = fetched_file + parse_key(key.rstrip('\n'))
        print 'All keys have been downloaded'
        download.write(base64.b64decode(fetched_file))
        print 'File has been decoded and saved as ', filename

# handle command line input

if len(sys.argv) < 3:
    print """Usage: ./pgpfs.py [action] filename1 filename2'
           action can be either ''store'' or ''fetch'''

       When action is 'store':
           filename1 is the file to upload, filename2 is the name of the key allocation table
       When action is 'fetch':
           filename1 is the key allocation table, filename2 is the output file

       Example uses:
         - To store 'sample.mp3' on the keyserver
           ./pgpfs.py store sample.mp3 sample.kat
         - To fetch the file contained in 'sample.kat' and store it as 'sample.mp3'
           ./pgpfs.py fetch sample.kat sample.mp3
    """
    sys.exit(0)

ACTION = sys.argv[1]

if ACTION not in ['store', 'fetch']:
    print 'Please specific either ''store'' or ''fetch'''
    sys.exit(0)

if ACTION == 'store':
    store_file(sys.argv[2], sys.argv[3])
elif ACTION == 'fetch':
    fetch_file(sys.argv[2], sys.argv[3])
