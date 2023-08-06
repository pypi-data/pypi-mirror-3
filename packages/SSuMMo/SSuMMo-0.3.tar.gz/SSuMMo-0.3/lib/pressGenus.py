#!/usr/bin/env python
"""
Script to find all the genuses present in the ARB database, get all of their HMMs,
and save all of those HMMs to a single file. Once all those HMMs are in a single
file, they're going to be pressed by hmmbuild.

"""


import MySQLdb
import os
import subprocess
import sys
import CONFIG
from threading import Thread
from Queue import Queue
import cPickle as pickle
from ssummolib import dict_walk

def getGenuses(domain):
        cnx = MySQLdb.connect(user=CONFIG.user,host=CONFIG.host,db=CONFIG.db,passwd=CONFIG.passwd)
        cur = cnx.cursor()
        cur.execute('SELECT tax_ID,Name,parentName from {0} where rank="genus" or rank="Genus";'.format( domain))
        try:
                for row in cur.fetchall():
                        yield row
        except TypeError:
                print row
                raise

class findHMMPath( Thread ):
    """This thread continually loops through the dictionary
    looking for path names that match the OTU names piped over.
    When the OTU name & parent name match, the path to that
    HMM is passed back to the main thread.
    """
    def __init__(self,tdict,inQ,outQ):
        Thread.__init__(self)
        self.tdict = tdict
        self.inQ = inQ
        self.outQ = outQ
#        self.l = lock
#        self.sem = sem
    def run(self):
        obj = self.inQ.get( )
        self.name, self.parentName = obj
        while True:
            for path,node in dict_walk(CONFIG.arbDBdir,self.tdict):
                taxPath = path.rsplit( os.path.sep,2 )
                if taxPath[-1] == self.name and taxPath[-2] == self.parentName:
                    self.inQ.task_done()
                    self.outQ.put( os.path.join( path, taxPath[-1] + '.hmm' ) )  # Pass path to HMM back to main process.
                    obj = self.inQ.get( )
                    if obj == 'END':
                        self.inQ.task_done()
                        break
                    else:
                        self.name, self.parentName = obj
            if obj == 'END':
                break

def pressHMM(inName):
        process = subprocess.Popen( [ 'hmmpress',inName],shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE )
        return process


if __name__ == '__main__':
        if len(sys.argv) == 1:
                print 'Going to press all genera from each domain, but...'
                domain = raw_input( 'Which domain?? [E]ukaryotes, [P]rokaryotes? or [c]ancel. [p]')
                if len(domain) == 0 or domain.startswith('p') or domain.startswith('P'):
                    domain = 'Prokaryotes'
                elif domain.startswith('e') or domain.startswith('E'):
                    domain = 'Eukaryotes'
                else:
                    print "Got {0}.\nExiting".format(domain)
                    exit()
        else:
                domain = sys.argv[1]
        outName = CONFIG.taxIndex[:CONFIG.taxIndex.rfind('.')] + '_to_press.hmm'  # Where to save all the genus HMMs.
        if domain != 'Eukaryotes' and domain != 'Prokaryotes':
                sys.stderr.write( "\n\nDon't recognise this as a domain:-\n  {0}\nExiting..\n".format( domain ) )
                exit()
        with file( CONFIG.taxIndex,'rb' ) as taxFile:
                sys.stdout.write( 'Loading the complete taxonomy index. . . ')
                tdict = pickle.load( taxFile )  ## Load the taxonomy index.
                print 'Done.'
        outFile = file( outName,'w' )    # Open output file.
        inQ = Queue()
        outQ = Queue()
        finder = findHMMPath( tdict, inQ, outQ)   # Initiate process.
        finder.start()                             # ditto.
        for taxID,OTU,parent in getGenuses( domain ):
                inQ.put( (OTU, parent) )
                path = outQ.get( )
                with file( path, 'r') as infile:  # Load the [genus name].hmm as a file handle.
                        outFile.write( infile.read() )  # Append the hmm file's contents to the output file [outName].

                outQ.task_done()
        inQ.put( 'END' )  # Close pipes.
        outQ.join()
        inQ.join()
        finder.join()
        outFile.close()
        print 'Found all {0} at genus. Pressing HMMs now into:-\n{1}.*.'.format(domain,outName)
        sys.stdout.write( 'Pressing all genera within {0} into:-\n{1}\n'.format( domain, outName )) # Tell user what's being made.
        process = pressHMM(outName)  # Press the HMM.
        return_code = process.wait()
        if return_code != 0:
                sys.stderr.write( 'hmmpress failed with this error:-\n' )
                sys.stderr.write( process.stdout.read() +  process.stderr.read() )
        os.remove( outName )
        

