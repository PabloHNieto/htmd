# (c) 2015-2016 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
from os.path import isdir, abspath, basename, exists,join
from os import getcwd, getlogin, makedirs, chdir
from subprocess import call,check_output
from htmd import UserInterface
import inspect
import shutil
#import pwd
import os

class LSF(UserInterface):
    _commands = {
       'name'      : None,                           # whatever identifier you want for the job
       'queue'     : "gpu_priority",                          # the 'queue' to run on
       'resources' : 'select[ngpus>0] rusage[ngpus_excl_p=1]',
       'memory'    : "4000",                           # MB
       'walltime'  : '23:59',                      # hh:mm:ss
       'executable': 'acemd',                        # The thing to run 
    }


    def __init__(self, **kw):
        for i in self._commands.keys():
            self.__dict__[i] = self._commands[i]

        for key,val in kw.items():
            if key in self._commands:
               self.__dict__[key] = val
            else:
               raise ValueError( "Invalid configuration option [%s]" % (key) )

        if not self.name:
             raise ValueError( "Name must be set" )
        # Find executables
        self._bsub = self._find_binary( "bsub" )
        self._bjobs = self._find_binary( "bjobs" )

        self._exe    = self._find_binary( self.executable )

    def _find_binary(self, bin ):
        ret = shutil.which( bin, mode=os.X_OK )
        if not ret:
           raise ValueError("Could not find required executable [%s]" % (bin) )
        ret=os.path.abspath(ret)
        return ret

    def retrieve(self):
        #Nothing to do as everything is in the same filesystem
        pass

    def wait( self ):
        from time import sleep
        import sys
        while self.inprogress() != 0:
            sys.stdout.flush()
            sleep(1)

    def submit(self, mydirs, debug=False ):
        '''SUBMIT - Submits all work units in a given directory list to
                     the engine with the options given in the constructor
                     opt.
             INPUT
                   - dirs: Directories which to submit.
        '''

        if isinstance(mydirs, str): mydirs = [mydirs]

        for d in mydirs:
            if not isdir(d):
                raise NameError('Submit: directory ' + d + ' does not exist.')

        # if all folders exist, submit
        for d in mydirs:
            dirname = os.path.abspath(d)
#            self.b = dirname
            if debug:
                print('Submitting ' + dirname)

            js = self._make_jobscript( dirname, self._exe )

            ret = 0
            cmd = [
              self._bsub,
              "-J", self.name,
              "-M", self.memory,
              "-W", self.walltime,
              "-q", self.queue,
              "-R", self.resources,
              "-n", "1",
              js
            ]
            if debug:
              print(cmd)
            try:
                ret = check_output( cmd )
                if debug:
                   print(ret)
            except:
               raise
               #raise ValueError( "Submission of [%s] failed" % (dirname) )



    def _make_jobscript( self, dir, exe ):
       fn = os.path.join( dir, "run.sh" )
       f = open(fn, "w")
       print("#!/bin/sh", file =f )
       print("cd \"" + dir + "\"", file=f)
       print("module load acemd", file=f )
       print("%s > log.txt 2>&1" % (exe), file=f )
       f.close()
       os.chmod( fn, 0o700 )
       return os.path.abspath(fn)

    def inprogress(self, debug=False):
        ''' INPROGRESS - Returns the sum of the number of running and queued
                      workunits of the specific group in the engine.

             SYNOPSIS
                   grid.inprogress()
             EXAMPLE
                   grid.inprogress()
        '''
        cmd = [ self._bjobs, "-J", self.name, "-sum", "-noheader" ]
        if debug:
           print(cmd)

        ret = check_output( cmd )
        if debug:
           print(ret.decode("ascii"))
        #TODO: check lines and handle errors
        l=ret.decode("ascii").split()
        return int(l[0]) + int(l[4])


if __name__ == "__main__":
    """
    s=LSF( name="adaptivetest" )
#    s.submit( "test/dhfr", debug=True )
#    s.submit( "test/dhfr", debug=True )
    ret= s.inprogress( debug=False )
    print(ret)
    pass
    """

