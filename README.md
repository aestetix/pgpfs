# PGP File System

PGP File System (pgpfs) is a tool to turn your friendly pgp keyserver into a
redundant persistant filesystem.

## Installation

From a base Ubuntu 14.04.5 installation, please install the following packages:

```
apt-get install git python-pip python-virtualenv rng-tools
```

Check out the repository onto your local machine:
```
git clone git@github.com:aestetix/pgpfs.git
```
This creates a directory called "pgpfs." Go into the directory and  run
```
virtualenv .
source bin/activate
pip install -r requirements.txt
```

## Usage
pgpfs is simple to use. It is able to both `store` and `fetch` documents from
the keyserver. Here are examples of usage:

### `store`
To store the file sample.mp3 and save the Key Allocation Table (kat) in
sample.kat, run:
```
python pgpfs.py store sample.mp3 sample.kat
```
This will create a file called sample.kat to be used when you want to retrieve
your file.

### `fetch`
To fetch the file sample.mp3 from the keyserver, assuming the kat file is called
sample.kat, run:
```
python pgpfs.py fetch sample.kat sample.mp3
```
