import urllib
import os
import random
import string
import tarfile
import shutil

def random_name():
    return ''.join([random.choice(string.letters) for i in range(0, 32)])

def download_temp(url):
    root = '/tmp/paxd-%s' % random_name()
    os.makedirs(root)
    archive = os.path.join(root, random_name() + '-archive.tar.gz')
    if url.startswith('file://'):
        shutil.copyfile(url[7:], archive)
    else:
        urllib.urlretrieve(url, archive)
    tar = tarfile.open(archive, mode='r:gz')
    tar.extractall(root)
    tar.close()
    os.unlink(archive)
    return root

def join(root, file):
    if file and file[0] == '/':
        file = file[1:]
    file = os.path.abspath(os.path.join(root, file))
    assert file.startswith(root), 'file must be within root directory'
    return file

