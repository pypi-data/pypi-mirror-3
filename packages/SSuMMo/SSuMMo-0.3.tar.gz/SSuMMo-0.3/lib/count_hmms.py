#!/usr/bin/env python
"""If called from a *nix shell, please provide the function name you want to 
call, and any required arguments, exactly as presented here.

e.g.
python count_hmms.py countseqs /path/to/dir

python count_hmms.py 
this will traverse all directories from
Archaea, Bacteria and Eukaryota, and will return the total number
of hmms that exist and the number that are in the right place.
"""
#   #####    ######   PRE-RAMBLE    ####    #####   #######
#
# Copyright (c) Alex Leach. 2011
# Contact: Alex Leach (albl500@york.ac.uk)
# University of York, Department of Biology,
# Wentworth Way, York YO10 4DU, United Kingdom
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have receive a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>
#
####    ****         END PRE-RAMBLE         ****    ####
##                                                     #
#
# Description:
#
#  Some functions to look through the SSUMMO directory structure, 
#    checking either the HMMs or the sequences found in that directory.
#  If a function argument is presented here with a default value, then
#    that argument is optional. Default values are the ones with an equal
#    sign. 
#  e.g. The function 'walkall' has an argument 'delete', which has a 
#   default value of False.
#
# Defined functions:-
#   walkall( dir_list = ['Bacteria','Eukaryota','Archaea'] , delete=False )
#   countseqs( pathname , file_name = 'accessions.txt'):
#   avseqlens( pathname ):
#   os_walk( dir_list, delete = False)
#   counthmms( cwd):
#
# Other help??:-
#   pydoc count_hmms.py
import os, sys
import CONFIG

def __init__( self ):
        #self.the_walk = self.the_walk()
        print "initiated count_hmms"

def walkall( dir_list = ['Bacteria','Eukaryota','Archaea'] , delete=False):
        """Walks all directories, tallying correctly placed hmm files.
        By default, don't delete misplaced hmms."""
        os_walk(dir_list, delete)

def countseqs( pathname , file_name = 'accessions.txt'):
        """Given a pathname to a taxonomic id,
        Return the number of representative 16S sequences in a
        taxonomies folder directory."""
        pathname = pathname.rstrip()
        if pathname[-1] == '/':
                pathname = pathname[:-1]
        if file_name == 'accessions.txt':
                try:
                        handle = file('{0}/accessions.txt'.format(pathname) ,'r')
                except IOError:
                        print "No accessions file at:- {0}/accessions.txt".format(pathname)
                        return 0
        else:
                with file( file_name ,'r') as sequence_file:
                        seq_count = 0
                        for line in sequence_file.xreadlines():
                                if line.startswith('>'):
                                        seq_count += 1
                return seq_count
        seq_count = 1
        for char in handle.readline():
                if char == ' ':
                        seq_count += 1
        return seq_count

def avseqlens( pathname ):
        """Given a pathname, find the sequences file, and average the 
        length of all the sequences"""
        from Bio import SeqIO, AlignIO
        tot_seq_lens = 0
        nseqs = 0
        try:
                handle = file('%s/sequences.fa' % pathname,'r')
                for sequence in SeqIO.parse(handle,'fasta'):
                        tot_seq_lens += len(sequence)
                        nseqs += 1
        except OSError:
                os.system('~/bin/blast/fastacmd -d %s -i %s/accessions.txt -o %s/sequences.fa' % ('/biol/people/albl500/454RDPstuff/blastDBs/arbDB', pathname, pathname))
                handle = file('%s/sequences.fa' % pathname,'r')
                for sequence in SeqIO.parse(handle,'fasta'):
                        tot_seq_lens += len(sequence)
                        nseqs += 1
        handle.close()
        print "Average sequence length in %s is %s" % (pathname, (tot_seq_lens/nseqs))
        try:
                handle = file('%s/alignment.fa' % pathname,'r')
                print "Figuring out the alignment sequence length of a %sMB file." % (os.path.getsize(pathname + '/alignment.fa') / 1000)
                alignment = AlignIO.read(handle, 'stockholm')
                print "Alignment length: %s" % (alignment.get_alignment_length())
        except IOError:
                print "no alignment file here. Not gonna make one either...."
        return (tot_seq_lens/nseqs)

def counthmms( cwd):
        """Given a pathname, this function will return the number of HMMs in that
        directory, and the number of directories in that directory"""
        contents = os.listdir(cwd)
        hmm_count = 0
        dir_count = 0
        for cont in contents:
                if cont.endswith('.hmm'):
                        hmm_count += 1
                elif '.' not in cont:
                        dir_count += 1
                else:
                        continue
        return hmm_count, dir_count
        
def os_walk( dir_list, delete = False):
        """Uses os.walk() and traverses the directories presented in the list
        'dir_list' and checks to see if hmms are present in the correct place.
        If delete is True, then these hmms will be deleted.
        If delete is False or not specified, then a count of misplaced hmms
        will be printed & returned.
        """
        hmm_count = 0
        dir_count = 0
        tot_hmm_count = 0
#       start_dir = '/biol/people/albl500/454RDPstuff/arbDB/'
        start_dir = CONFIG.arbDBdir
        print 'starting from {0}'.format(CONFIG.arbDBdir)
        if type(dir_list) == str and os.path.exists(dir_list):
                dir_list = [dir_list]
        for _dir in dir_list:
                _dir = os.path.join(start_dir, _dir )

                for root, dirs, files in os.walk(_dir):
                        dir_count += 1
                        path = root
                        end_path = path[path.rfind('/')+1:]
                        hmm_true = False    ### Initiate variable that tests if .hmm file in correct place
                        for fil in files:
#                               hmm_true = False    ### Initiate variable that tests if .hmm file in correct place.
                                if fil.endswith('.hmm'):
                                        if fil[:fil.rfind('.')] == end_path:
                                                hmm_count += 1
                                                hmm_true = True
                                        else:
                                                if delete == True:
                                                        os.remove( os.path.join(root,fil) )
                                                        print "removed '{0}'".format(os.path.join(root , fil) )
                                                else:
                                                        print "would remove '{0}'".format(os.path.join(root , fil ))
                                        tot_hmm_count += 1
                                        if hmm_true == False:
                                                print os.pathjoin(root,fil), "doesn't have hmm in correct place"
                        if hmm_true == False:
                                print root

        print 'num of dirs = {0}'.format(dir_count)
        print 'num of hmms in correct place = {0}'.format(hmm_count)
        print 'total number of HMMs = {0}'.format(tot_hmm_count)


if __name__ == '__main__':
        dir_list = ['Bacteria','Eukaryota','Archaea']
        try:
                fn = sys.argv[1]
        except IndexError:
                error = '\n\nWrong number of arguments specified. To see the documentation, try:-'
                error += '\n$ pydoc {0}\n'.format( __file__ )
                sys.stderr.write( error)
                exit()
        if len(sys.argv) == 4:
                arg = sys.argv[2]
                arg2 = sys.argv[3]
        elif len(sys.argv) == 3:
                arg = sys.argv[2]
        if fn == 'walkall':
                try:
                        walkall(dir_list = arg, delete=False)
                except NameError:
                        try:
                                walkall(arg)
                        except NameError:
                                walkall()
        elif fn == 'countseqs':
                print countseqs(arg)
        elif fn == 'counthmms':
                counthmms(arg)
        elif fn == 'os_walk':
                if len(sys.argv) >= 4:
                        os_walk(arg, arg2)
                else:
#               except KeyError,NameError:
                        os_walk(arg)
        elif fn == 'avseqlens':
                avseqlens(arg)
        else:
                print "Unknown function. Functions are:-"
                print "walkall, countseqs, counthmms & os_walk"

