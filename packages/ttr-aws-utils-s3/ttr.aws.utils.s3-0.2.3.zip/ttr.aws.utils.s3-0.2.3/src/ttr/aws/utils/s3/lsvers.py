# Copyright (c) 2011, Jan Vlcinsky
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
import datetime
import textwrap
import itertools
import dateutil.parser
import plac
import os

class HtmlTemplate():
    """Class handling creation of html chart.
    Use:
    1. html = HtmlTemplate(fname, ...)
    2. loop through items, and for each item:
        html.write_line(...)
    3. when finished, close it:
        html.close()
    html header and footer are written out automatically.
    """

    header = """
<html>
  <head>
    <script type='text/javascript' src='https://www.google.com/jsapi'></script>
    <script type='text/javascript'>
      google.load('visualization', '1', {{'packages':['annotatedtimeline']}});
      google.setOnLoadCallback(drawChart);
      function drawChart() {{
        var data = new google.visualization.DataTable();
        data.addColumn('datetime', 'Date Time');
        data.addColumn('number', '{set_1_name}');
        data.addColumn('number', '{set_2_name}');
        data.addRows(["""
    row = "[new Date({year}, {month}, {day}, {hour}, {minute}, {second}), {size}, {age}],"
    footer = """]);
        var chart = new google.visualization.AnnotatedTimeLine(document.getElementById('chart_div'));
        chart.draw(data,
  {{'displayAnnotations': true, 
  'scaleType': 'allmaximized',
  'scaleColumns': [0,1]}}
);
      }}
    </script>
  </head>
  <body>
      <h2>{title}</h2>
      <h3>{subtitle}</h3>
    <div id='chart_div' style='width: 1200px; height: 700px;'></div>
    <div>Wait, untill the chart loads, it takes some seconds till you see it...(this messsage will stay here even when chart loaded)</div>
  </body>
</html>"""
    def __init__(self, f, title, subtitle, set_1_name, set_2_name):
        self.f = f
        self.title = title
        self.subtitle = subtitle
        self.set_1_name = set_1_name
        self.set_2_name = set_2_name
        #in case the file cannot be open, it throws exception and the instance shall not be created   
        self._write_header()
        return

    def close(self):
        self._write_footer()
        self.f.close()
        return

    def _write_header(self):
        self.f.write(self.header.format(title=self.title, subtitle=self.subtitle, set_1_name=self.set_1_name, set_2_name=self.set_2_name))
        return

    def write_line(self, time, size, age):
        line = self.row.format(year=time.year,
                              month=time.month - 1,
                              day=time.day,
                              hour=time.hour,
                              minute=time.minute,
                              second=time.second,
                              size=size,
                              age=age)
        self.f.write(line)
        return

    def _write_footer(self):
        self.f.write(self.footer.format(title=self.title, subtitle=self.subtitle, set_1_name=self.set_1_name, set_2_name=self.set_2_name))
        return

@plac.annotations(
    from_time=("Modification time of oldest expected version expressed in ISO 8601 format. Can be truncated. (default: goes to the oldest version)", "option", "from"),
    to_time=("Modification time of youngest expected version expressed in ISO 8601 format. Can be truncated. (default: goes to the latest version)", "option", "to"),
    list_file=("Name of file, where is result written in csv format. If set, the file is always overwritten.", "option", None, argparse.FileType("wb")),
    html_file=("Name of file, where is result written in html format (as a chart). If set, the file is always overwritten.", "option", None, argparse.FileType("wb")),
    version_id=('''Optional version-id. If specified, listing does not start from the freshest version, but starts searching from given VERSION_ID
        and continues searching older and older versions.
        This could speed up listng in case, you need rather older files and you know VERSION_ID which came somehow later
        then is the time scope you are going to list.''', "option"),
    bucket_name=("name of AWS S3 bucket, which is searched.", "positional"),
    key_name=("""name of key to list. Typically it is complete name of a key, but also truncated name can be set, in this case
        all keys, sharing this prefix, will be listed.""", "positional")
)
def main(bucket_name, key_name, from_time=None, to_time=None, list_file=None, html_file=None, version_id=None, ):
    """Lists all versions of given key, possibly filtering by from - to range for version last_modified time.
    Allows to put the listing into csv file and or into html chart.
    
        Listing shows:
          key_name
            "file name". Can repeat if the file has more versions

          version_id
            unique identifier for given version on given bucket. Has form of string and not a number. identifiers are "random", do not
            expect that they are sorten alphabetically.

          size
            size of file in bytes

          last_modified
            ISO 8601 formated time of file modification, e.g. `2011-06-22T03:05:09.000Z`

          age
            difference between last_modified or given version and preceding version.
            It is sort of current update interval for that version.
        
        Sample use:
        Lists to the screen all versions of file keynme in the bucketname bucket::

            $ s3lsvers bucketname keyname

        Lists all versions younger then given time (from given time till now)::

            $ s3lsvers -from 2011-07-19T12:00:00 bucketname keyname

        Lists all versions older then given time (from very first versin till given date)::

            $ s3lsvers -to 2011-07-19T12:00:00 bucketname keyname

        Lists all versions in period betwen from and to time::

            $ s3lsvers -from 2010-01-01 -to 2011-07-19T12:00:00 bucketname keyname

        Lists all versions and writes them into csv file named versions.csv::

            $ s3lsvers -list-file versions.csv bucketname keyname

        Lists all versions and writes them into html chart file named chart.html::

            $ s3lsvers -html-file chart.html bucketname keyname

        Prints to screen, writes to csv, creates html chart and this all for versions in given time period.::

            $ s3lsvers -from 2010-01-01 -to 2011-07-19T12:00:00 -list-file versions.csv -html-file chart.html bucketname keyname
    
    """
    cmdname = os.path.basename(sys.argv[0])
    print("{now} - {cmdname}.".format(now=datetime.datetime.now(), cmdname=cmdname))
    if (from_time and to_time) and (from_time > to_time):
        print "-from ({from_time}) must be smaller then -to ({to_time})".format(**locals())
        return

    conn = boto.connect_s3() #todo: allow to use explicit credential command line values for aws_key_id and aws_secret_key
    bucket = conn.get_bucket(bucket_name)
    try:
        if version_id == None: #todo
            raise NameError
        versions = bucket.list_versions(key_name, key_marker=key_name, version_id_marker=version_id)
    except NameError:
        versions = bucket.list_versions(key_name)
    try:
        if html_file:
            title = "{bucket_name}:{key_name}".format(**locals())
            subtitle = "(gzipped) feed size [bytes] and update intervals[seconds]"
            set_1_name = "Feed size"
            set_2_name = "Update iterval"
            html = HtmlTemplate(html_file, title=title, subtitle=subtitle, set_1_name=set_1_name, set_2_name=set_2_name)
 
        vers_a, vers_b = itertools.tee(versions)
        vers_b.next()
        for i, ka, kb in itertools.izip(itertools.count(), vers_a, vers_b):
            last_modified = ka.last_modified
            atime = dateutil.parser.parse(last_modified)
            btime = dateutil.parser.parse(kb.last_modified)
            age = (atime - btime).seconds
            if from_time and (last_modified < from_time):
                break
            elif to_time and (last_modified > to_time):
                if i % 600 == 0:
                    print "version num: %d, modified: %s" % (i, last_modified)
                continue
            print("Name: {0} Date: {1} Version: {2} Size: {3} Age: {4}".format(ka.name, ka.last_modified, ka.version_id, ka.size, age))
            if list_file:
                line = "{key_name};{version_id};{size};{last_modified};{age}\n"
                line = line.format(key_name=ka.name, version_id=ka.version_id, size=ka.size, last_modified=ka.last_modified, age=age)
                list_file.write(line)
            if html_file:
                html.write_line(atime, ka.size, age)                   
        print("{now} - {cmdname} completed listing versions.".format(now=datetime.datetime.now(), cmdname=cmdname))
    except KeyboardInterrupt:
        print "...cancelled."
        pass
    finally:
        try:
            list_file.close()
        except:
            pass
        try:
            html.close()
        except:
            pass
    return
    
def placer():
    try:
        plac.call(main)
    except Exception as e:
        print e
    
if __name__ == "__main__":
    placer()
