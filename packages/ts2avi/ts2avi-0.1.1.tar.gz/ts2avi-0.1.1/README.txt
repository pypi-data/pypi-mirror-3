========
 ts2avi
========

Other languages : `fr <LISEZMOI.html>`_

Introduction
--------------------------------------------------------------------

Boxes like the freebox provided by the french ISP "free" allow 
recording of TV channels. Such records are encoded using an internal
vlc service in *Transport Stream* format. Usually for a common 2h
movie the size of the records can reach 3 to 4Gb -- and if you 
intend to record at least 2 movies each week then you will reach 
your hard disk capacity sooner than expected!

`ts2avi` is a python script that will allow conversion of all your
ts videos into a common divx container (with MPEG4 for video format
and MP3 for audio format). The sizes of the produced video files
are 4 to 6 times lesser than the original ones -- with however a
minimum degradation of image quality.

Prerequisites
--------------------------------------------------------------------

ts2avi being a python script, of course you will need a recent 
installation of python. It is recommended to have a 2.7 version 
although the script might work with a 2.6 version, as it uses the
subprocess module.

For video conversion the script relies on `mencoder`, please check 
that it is installed or download it from 
http://www.mplayerhq.hu/design7/dload.html.
For most GNU/Linux distributions it should be available alongside 
with mplayer.

ts2avi is at present working only for linux-based platforms. However
it can be easily tuned for MS Windows ones, if the prerequisites are
installed, but it should need a small tuning of the script to 
overwrite the default path for `mencoder`.


Installation
--------------------------------------------------------------------

The ts2avi script is shipped as a distutils package. To install
the library, unpack the distribution archive, and issue the 
following command::

    $ python setup.py install

If you want to have a *local* installation of the script, or 
equivalently if you don't have root access for installing 
site-packages, you may want to make benefit from the new 'user'
option which is provided by recent versions of distutils::

    $ python setup.py install --user

This will install everything in your ``$HOME/.local`` directory for 
POSIX users. Don't forget to add your ``$HOME/.local/bin`` to your
path for instance in you `.bashrc` source bash configuration file.

You might also install ts2avi as an egg package using the 
setuptools `easy_install` script::

    $ easy_install ts2avi

would do everything for you: download and install ts2avi.

Usage
--------------------------------------------------------------------

Basic usage is as follows::

    $ ts2avi.py <myrecord>.ts

This would convert the argument TS file into an MPEG4 <myrecord>.avi 
file in the same current directory. Please notice that the script 
recognizes all current Unix pattern expansion, so for instance if 
you would like to convert all records from a given TV channel::

    $ ts2avi.py TMC*.ts

For storage of output files in a different directory, which could be
usefull if you intend to copy the avi files on an external hard disk
for instance, use the `--output_dir` option::

    $ ts2avi.py --output_dir=/media/hdd/Videos *.ts

Video conversion is done using different profiles (see `How it works`_).
To select a given profile issue the following command::

    $ ts2avi.py --profile='fast' <myrecord>.ts

For full explanation on the different options of ts2avi, try::

    $ ts2avi.py --help

How it works
--------------------------------------------------------------------

For each argument file, the video conversion is performed in a 
temporary directory. The different steps are the followings:

1. The container is transformed into MPEG (audio and video 
   encoding are however totally preserved during this operation,
   it is a pure copy)
   
2. Audio is extracted and converted separatly into MP3

3. Finally a video encoding into MPG4 is performed using a two
   pass process.

Different profiles are available however. To select one of them,
use the `--profile` option. The previous steps refer to the 
default profile which is supposed to provide the best quality 
possible.

Drawbacks (v. 0.1.1)
--------------------------------------------------------------------

- For the moment, the script is working on Unix-like platforms. 
  Tuning it for MS Windows is however not very complicated: just 
  use the '--mencoder_path' option to set the precise path to your
  local installation of `mencoder`.
  
- Multiprocessing is not working at present. This could be usefull
  since video conversion can last several hours especially when
  converting more than one video files. This will be probably 
  developped in a further version by using the multiprocessing
  python module.
  
- The original files are not deleted after conversion, and won't be
  either in a further version. This is done on purpose, just in case
  the quality of the converted video is not good enough, and you would
  like to try another profile.

- Of course, ts2avi will not remove advertising. For that purpose, 
  use some video editor like 
  `Avidemux <http://avidemux.sourceforge.net>`_.
  Performing this operation *before* the video conversion is even 
  better since you will gain the time due to advertising conversion.

TODO (v. 0.1.1)
--------------------------------------------------------------------
  
- allow the user to define its own profiles in a "ts2avi.ini" file

- adjust error treatment

- instead of using the python `print` command, make use of the
  `logging` module
  
- allow multiple conversions at the same time using the 
  `multiprocessing` python module
  


