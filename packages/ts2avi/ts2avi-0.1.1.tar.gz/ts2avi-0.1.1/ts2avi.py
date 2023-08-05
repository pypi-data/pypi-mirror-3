#!/usr/bin/python
# coding: utf-8

import glob
from optparse import OptionParser
import os
from subprocess import Popen, STDOUT
import shutil
import sys
import tempfile
import traceback

#------------------------------------------------------------------------------

profiles = {
    "default": {
        "mencoder": "/usr/bin/mencoder",
        "globalopts": ["-quiet",],
        "lavcopts_pass1": "vcodec=mpeg4:vpass=1",
        "lavcopts_pass2": "vcodec=mpeg4:mbd=2:trell:vpass=2",
        "lameopts": "vbr=3",
    },
    "fast": {
        "mencoder": "/usr/bin/mencoder",
        "globalopts": ["-quiet",],
        "lavcopts_pass1": "vcodec=mpeg4:vpass=1",
        "lavcopts_pass2": "vcodec=mpeg4:vpass=2",
        "lameopts": "vbr=3",
    }

}

def list_profiles(option, opt, value, parser):
    message = "Available profiles"
    message += "\n" + len(message)*"-" + 2*"\n"
    for key,val in profiles.items():
        message += key + ":\n\t"
        message += "\n\t".join(["%s: %s" % (key2,val2) \
                    for (key2,val2) in val.items()])
        message += 2*"\n"
    print "\n" + message
    sys.exit(0)
    
    

#------------------------------------------------------------------------------

usage = "usage: %prog [options] arg"
parser = OptionParser(usage=usage)
parser.set_defaults(verbose=True)
parser.set_defaults(clean=False)
parser.set_defaults(profile="default")
parser.set_defaults(output_dir=os.getcwd())
parser.add_option("-p", "--profile",
                  action="store", type="string", dest="profile",
                  help="Profile for conversion to be used")
parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose",
                  help="Verbose output")
parser.add_option("-o", "--output_dir",
                  action="store", type="string", dest="output_dir",
                  help="Specifies an output directory for the produced avi files")
parser.add_option("-c", "--clean",
                  action="store_true", dest="clean",
                  help="Cleans temporary directories after processing")
parser.add_option("-t", "--threads",
                  action="store", type="int", dest="nthreads",
                  help="Launches n threads at the same time")
parser.add_option("-l", "--list-profiles",
                  action="callback", callback=list_profiles,
                  help="List the available profiles for conversion")
parser.add_option("-m", "--mencoder_path",
                  action="store", type="string", dest="mencoder_path",
                  help="Overwrite the default mencoder path in the profile")


#------------------------------------------------------------------------------

class ConvertToAvi:
    _sep = 79*"-"

    def __init__(self, file, **kwargs):
        self._roottmpdir = tempfile.mkdtemp()
        self._cwd = os.getcwd()
        self.profile = profiles[kwargs['profile']]
        if kwargs['mencoder_path']:
            self.profile['mencoder'] = kwargs['mencoder_path']
        self.output_dir = kwargs['output_dir']
        self.file = os.path.abspath(file)
        self._pass = 0
        self._process = None
        basename = os.path.splitext(os.path.basename(self.file))[0]
        self._mpgfile = basename + ".mpeg"
        self._avifile = basename + ".avi"
        self.final_avifile = os.path.join(self.output_dir, self._avifile)
        self._logfile = None
        print self._sep
        print "Treated file:\n\t", self.file
        print "Temporary directory:\n\t", self._roottmpdir
        print "Intermediate MPEG file:\n\t" + self._mpgfile
        print "Target AVI file:\n\t" + self.final_avifile
        print self._sep

    def status(self):
        return (self._pass, self._process.poll())

    def wait(self):
        return self._process.wait()

    def run_pass(self, args, message=""):
        mencoder = self.profile['mencoder']
        gopts = self.profile['globalopts']
        logfilename = "pass_%i.log" % self._pass
        self._logfile = open(logfilename, "w")
        print "Pass %i: %s" % (self._pass, message)
        self._process = Popen([mencoder,] + args + gopts,
                              stdout=self._logfile, stderr=STDOUT)
        retcode = self.wait()
        self._logfile.close()
        return retcode

    def clean(self):
        pass

    def run(self):
        try:
            # initialization: the ts file container is converted to mpeg
            print "Entering temporary directory %s" % self._roottmpdir
            os.chdir(self._roottmpdir)
            args = ["-oac", "copy", "-ovc", "copy", "-of", "mpeg",
                    "-o", self._mpgfile, self.file]
            retcode = self.run_pass(args, "Converting to mpeg...")

            # first pass: the audio is first converted to mp3 without
            # affecting video
            self._pass += 1
            args = ["-ovc", "frameno", "-oac", "mp3lame", "-lameopts",
            self.profile["lameopts"],
                        "-o", "frameno.avi", self._mpgfile]
            retcode = self.run_pass(args, "Converting audio...")

            # second pass: corresponds to the first pass of video encoding
            self._pass += 1
            args = ["-ovc", "lavc", "-lavcopts",
            self.profile["lavcopts_pass1"], "-oac", "copy",
                        "-o", self._avifile, self._mpgfile]
            retcode = self.run_pass(args, "First video encoding...")

            # third pass: corresponds to the second (and last) pass of video
            # encoding
            self._pass += 1
            args = ["-ovc", "lavc", "-lavcopts",
            self.profile["lavcopts_pass2"], "-oac", "copy",
                        "-o", self._avifile, self._mpgfile]
            retcode = self.run_pass(args, "Second video encoding...")
        except:
            sys.stderr.write("Error during pass %i" % self._pass)
            traceback.print_exc()
            sys.exit(1)
        finally:
            os.chdir(self._cwd)

        print "Done converting\n" + self._sep
        # the created avi file is moved to the current directory
        shutil.copy2(os.path.join(self._roottmpdir, self._avifile),
                    self.final_avifile)
        print self._sep


def main():
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("incorrect number of arguments")

    # processing for each argument without forgetting first to expand all
    # arguments using the *nix-like expansion with glob
    args = reduce(lambda x,y:x+y, map(glob.glob, args))

    # launches the conversion for each argument
    for arg in args:
        print "Converting file %s" % (arg)
        this_convert = ConvertToAvi(arg, **options.__dict__)
        this_convert.run()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    main()





