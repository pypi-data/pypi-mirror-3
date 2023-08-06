# Copyright (c) 2012, TamTam Research s.r.o. http://www.tamtamresearch.com
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met: 
# 
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer. 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution. 
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies, 
# either expressed or implied, of the FreeBSD Project.

import boto
import argparse
import sys
import plac
import csv
from itertools import izip, count
import dateutil.parser
import os.path
from StringIO import StringIO
import gzip
import time

def gunzip_data(data):
    '''Decomress data from string using gzip method.

    :type data: string
    :param data: string to be decompressed
    
    :rtype: string
    :return: decompressed string
    '''
    buf = StringIO(data)
    gzipper = gzip.GzipFile(fileobj=buf)
    data = gzipper.read(data)
    gzipper.close()
    #todo, check for possible memory leak, shall I close the buf?
    return data



@plac.annotations(
    bucket_name=("bucket name (default: %(default)s)", "positional"),
    csv_version_file=("name of CSV file with version_id", "positional", None, argparse.FileType("rb")),
    output_version_id_names=("Resulting file names shall use version_id to become distinguished (default is to use timestamp of file creation)", "flag"),
    no_decompression=("Keeps the files as they come, do not decompress, if they come compressed", "flag")
)
def main(bucket_name, csv_version_file, output_version_id_names = False, no_decompression=False):
    """Fetch file versions as listed in provided csv file
    
    Typical csv file (as by default produced by s3lsvers) is:
    
        my/versioned/feed.xml;OrUr6XO8KSKEHbd8mQ.MloGcGlsh7Sir;191345;2012-05-23T20:45:10.000Z;39
        my/versioned/feed.xml;xhkVOy.dJfjSfUwse8tsieqjDicp0owq;192790;2012-05-23T20:44:31.000Z;62
        my/versioned/feed.xml;oKneK.N2wS8pW8.EmLqjldYlgcFwxN3V;193912;2012-05-23T20:43:29.000Z;58

    and has columns:
    :key_name: name of the feed (not containing the bucket name itself)
    :version_id: string, identifying unique version. Any following columns can contain anything.
    :size: size in bytes. This column is not used and can be missing.
    :last_modified: date, when the version was posted. This column is not used and can be missing.
    
    Typical use (assuming, above csv file is available under name verlist.csv)::
    
        $ %(prog)s yourbucketname verlist.csv
    
    What will create following files in current directory:
    
    * my/versioned/feed.xml.2012-05-23T20_45_10.xml
    * my/versioned/feed.xml.2012-05-23T20_44_31.xml
    * my/versioned/feed.xml.2012-05-23T20_43_29.xml
    
    Even though these files are gzipped on server, they will be decompressed on local disk.
    
    """
    try:
        conn = boto.connect_s3() #todo: allow to use explicit credential command line values for aws_key_id and aws_secret_key
        bucket = conn.get_bucket(bucket_name)
    except:
        print "Problem to connect to bucket or buckeet missing. Check your credentials (e.g. using BOTO_CONFIG)"
        return
    try:
        for i, row in izip(count(), csv.reader(csv_version_file, delimiter = ";")):
            key_name, version_id = row[:2]
            print "{i:2d}: key_name: {key_name}, version_id: {version_id}".format(**locals())
            key = bucket.get_key(key_name, version_id = version_id)
            last_modified = dateutil.parser.parse(key.last_modified)
            fname, ext = os.path.splitext(os.path.basename(key_name))
            if output_version_id_names:
                verpart = key.version_id
            else:
                verpart = "{last_modified:%Y-%m-%dT%H_%M_%SZ}".format(last_modified = last_modified)
            fname = "{fname}.{verpart}{ext}".format(**locals())
            with open(fname, "wb") as f:
                if (key.content_encoding in ("deflate", "gzip")) and (not no_decompression):
                    f.write(gunzip_data(key.get_contents_as_string()))
                else:
                    key.get_contents_to_file(f)
            #try to set modification time to the time, version was created in bucket.
            tm = time.mktime(last_modified.timetuple())
            os.utime(fname, (tm, tm))
            print "resulting file name: {fname}".format(fname = fname)
    except KeyboardInterrupt:
        print "...terminated."
        
    return

def placer():
    plac.call(main)
    
if __name__ == "__main__":
    plac.call(main)