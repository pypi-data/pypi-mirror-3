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

from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()


version = '0.2.3'

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
    "setuptools",
    "boto",
    "argparse",
    "python-dateutil==1.5",
    "plac"
]

setup(name='ttr.aws.utils.s3',
    version=version,
    description="Some command lines utilities to interact with files stored in AWS S3 incl. versioned ones.",
    long_description=README + '\n\n' + NEWS,
    classifiers=[
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 3 - Alpha"         ,
        "Environment :: Console"                  ,
        "License :: OSI Approved :: BSD License"  ,
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX"               ,
        "Programming Language :: Python :: 2.6"   ,
        "Programming Language :: Python :: 2.7"   ,
        "Topic :: Communications :: File Sharing" ,
        "Topic :: System :: Archiving"            ,
        "Topic :: System :: Archiving :: Backup"  ,
        "Topic :: System :: Recovery Tools"       ,
        "Topic :: Utilities"                      ,
    ],
    keywords='aws s3 boto',
    author='Jan Vlcinsky',
    author_email='jan.vlcinsky@tamtamresearch.com',
    url='https://bitbucket.org/vlcinsky/ttr.aws.utils.s3',
    license='BSD',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages = ['ttr', 'ttr.aws', 'ttr.aws.utils'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            ['s3lsvers=ttr.aws.utils.s3.lsvers:placer', 's3getvers=ttr.aws.utils.s3.getvers:placer']
    }
)
