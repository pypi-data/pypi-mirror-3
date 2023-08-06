#!/usr/bin/env/python
"""
Description:

Class to work with alignments from the ARB database.
Their alignments are big and some of the sequences contain gaps.
This can output those sequences and give the option of whether to
keep those gaps or not.

Example:-
python ArbIO.py SSU_Ref_104_full_align.fasta 


"""
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
# Description:
# 
# Class to work with alignments from the ARB database.
# Their alignments are big and some of the sequences contain gaps.
# This can output those sequences and give the option of whether to
# keep those gaps or not.
#
# Example:-
# python ArbIO.py SSU_Ref_104_full_align.fasta 

import sys
import re
import os
import cPickle as pickle
from Bio import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Alphabet import generic_rna

class arbSeqRecord( SeqRecord ):
    def __init__(self,seq,**kwargs):
        SeqRecord.__init__(self,seq,**kwargs)
        self.index = {}
    def __del__(self):
        """Clean up method. Called on garbage collection"""
    def storeindex(self,index):
        self.index.update( { self.id : index } )
    def tell(self):
        return self.index[self.id]
class DotsException( Exception ):
        pass

class ArbIO( object ):
        """Works with large files...
        Keep the file object open, and move around using the ArbIO.index
        This contains byte locations of each record, but if indexed, then
        the sequence will be returned."""
        def __init__(self,inHandle=sys.stdin,out=sys.stdout,index=None):
                if type(inHandle) == file:
                        self.inFile = inHandle
                elif type(inHandle) == str and os.path.exists(inHandle):
                        self.inFile = file(inHandle,'r')
                else:
                        raise IOError("{0} not a handle or valid filename".format(inHandle))
                self.taxonomy = {}
                self.indexes = {}
                if type(out) == file and out != sys.stdout:
                        self.outFile = out
                        prefix = out.name[:out.name.rfind('.')]
                elif type(out) == str and not os.path.exists(out):
                        print "Saving output sequences to '{0}'".format(out)
                        self.outFile = file(out,'w+r')
                        prefix = out[:out.rfind('.')]
                elif type(out) == str:
                        prefix = out[:out.rfind('.')]
                        if raw_input("Are you sure you want to overwrite '{0}'?".format(out)) == 'y':
                                self.outFile = file(out,'w+r')
                        else:
                                print "Exiting..."
                                exit()
                else:
                        prefix = self.inFile.name[:self.inFile.name.rfind('.')]
                        self.outFile = None
                self.bracketSpecies = re.compile( r'(?<=[\[]{1})[\w\s]+(?=\]$)' )
                if index:
                        indexName = prefix + '.pklindex'
                        if os.path.exists( indexName ) and os.path.getsize( indexName ) > 0:
                                with file(indexName,'rb') as self.indexFile:
                                        self.indexes = pickle.load(self.indexFile)
                                        self.indexFile = None
                        else:
                                self.indexFile = file(indexName,'wb')
                                self.indexes = self.index()
                else:
                        self.indexFile = None
                        self.indexes = self.index( )
                self.dotsNspaces = re.compile(r'[\s\.]+')

        def __del__(self):
                self.inFile.close()
                if type(self.outFile) == file and not self.outFile.closed:
                        self.outFile.close()
                if type(self.indexFile) == file and self.indexFile.mode == 'wb' and not self.indexFile.closed:
                        print "Pickling {0} to {1}".format(str(len(self.indexes))+' sequence indexes',self.indexFile.name)
                        pickle.dump(self.indexes , self.indexFile,-1 )
                        self.indexFile.close()
                elif type(self.indexFile) ==file and not self.indexFile.close:
                        self.indexFile.close()

        def __getitem__(self,accession):
                location = self.indexes[accession]
                self.inFile.seek(location)
                line = self.inFile.readline()
                if line[:1] == '>':
                        id, species, desc = self.parseHeader( line )
                        if id != accession:
				sys.stderr.write( """Index Corrupt. Run dictify.py --indexSeqs again.
						Expected {0}
						Got {1}
						Whole line:-
						{2}""".format( accession ,id,line ) )
				raise IndexError
                else:
                        print line
                        raise ValueError("Index Corrupt. Run dictify.py --indexSeqs")
                sequence = ''
                while True:
                        line = self.inFile.readline()
                        if line[:1] == '>' or len(line)== 0:
                                break
                        else:
                                sequence += line.rstrip()
                return arbSeqRecord( Seq.Seq(sequence,alphabet = generic_rna),id=id,name=species,description=desc)

        def __setitem__(self,accession,location):
                self.indexes.update( { accession : location } )

        def rereplace(self,regObj):
                groups = regObj.groups()
                if groups[0]:
                        return ''
                elif groups[2]:
                        return '-'* regObj.group().count('.')

        def regreplace(self,matchObject):
                if matchObject.start() == 0 or matchObject.end() == len(matchObject.string):
                        return '-' * matchObject.group().count('.')
                elif '.' in matchObject.group():
                        raise DotsException()
                return ""

        def arbSeqToStr(self,sequence,skipGapped=True):
                try:
                        return self.dotsNspaces.sub(self.regreplace,sequence)
                except DotsException:
                        if not skipGapped:
                                return self.dotsNspaces.sub( lambda m: '-' * m.group().count('.'), sequence)
                        else:
                                return None

        def close(self):
                """Closes 3 open handles:-
                self.inFile,
                self.outFile,
                self.indexFile (if it's open, dumping contents of self.indexes there)"""
                self.__del__()
        def index(self):
                """ Indexes self.inFile for sequence locations.
                Dumps the index to self.indexFile, which is named with the same prefix as
                self.inFile, but with '.pklindex' as the suffix."""
                self.inFile.seek(0)
                while True:
                        prevLineLocation = self.inFile.tell()
                        line = self.inFile.readline()
                        if line[:1] == '>':
                                accession,name,desc = self.parseHeader(line[1:])
                                self[accession] = prevLineLocation
                        elif len(line) == 0:
                                break
                        else:
                                continue
                return self.indexes
        def indexAndInfo(self):
                """ Indexes self.inFile for sequence locations, whilst
                creating dictionaries containing the sequence header
                information.
                If a species is presented in [ ... ], this is stored in
                a dictionary called self.speciesDict, with accessions
                as the keys.
                Everything else in a sequence header is stored in another
                dictionary self.info
                """
                self.inFile.seek(0)
                self.info = {}
                count = 0
                while True:
                        prevLineLocation = self.inFile.tell()
                        line = self.inFile.readline()
                        if line[:1] == '>':
                                accession,name,desc = self.parseHeader(line[1:])
                                self[accession] = prevLineLocation
                                self.info.update( { accession : { 'desc' : desc } } )
                                if len(name)>0:
                                        self.info[accession].update( { 'species': name } )
                                count += 1
                        elif len(line) == 0:
                                break
                        else:
                                continue
                return count

        def FastaIterator(self,skipGapped=True):
                for SeqRec in self.parse(self.inFile,skipGapped):
                        yield SeqRec.format('fasta')
                self.indexed = True
        
        def fetch(self,accessions):
                """Give a list of accessions and this will yield them as SeqRecord objects
                by reading them from the rewritten file."""
                for accession in accessions:
                        yield self[accession]

        def parseHeader(self,seqHeader):
                """Given the header of an ARB sequence or fasta sequence,
                will return the tuple:-
                (id,name,description).
                id is the everything up until the first bit of whitespace.
                description is the rest up until '[' if found.
                name is anything that's in the square brackets."""
                if seqHeader[:1] == '>':
                        header = re.split('\s',seqHeader[1:],1)
                else:
                        header = re.split('\s',seqHeader,1)
                if type(header) == list and len(header) == 2:
                        id, desc = header[0], header[1].rstrip()
                elif type(header) == list and len(header) == 1:
                        id,desc = header,''
                else:
                        raise TypeError("Unable to parse sequence header: {0}".format(seqHeader))
                species = re.search( self.bracketSpecies ,desc)
                if species:
                        name = species.group()
                        desc = desc[:species.start()-1].rstrip()
                else:
                        name = ''
                return (id,name,desc)

        def parse(self,handle,skipGapped=True):
                """ An iterator function that yield's SeqRecord objects from an ARB sequence
                alignment.
                Parsing includes converting dots '.' at the start and end of each alignment to
                dashes '-'. 
                Also, will check for dots in the middle of the sequence, which represent gaps
                in the alignment. If these dots are found and skipGapped=True (default), then
                these SeqRecords will not be yielded.
                """
                sequence = ''
		line = handle.readline()
		assert line.startswith('>')
		id,name,desc = self.parseHeader(line.rstrip())
                for line in handle:
                        if line.startswith('>'):
                                #if sequence != '':
				sequence = self.arbSeqToStr(sequence,skipGapped)
				record = arbSeqRecord( Seq.Seq(sequence,alphabet = generic_rna),id=id,name=name,description=desc)
				yield record
				# end if block
                                id,name,desc = self.parseHeader(line.rstrip())
                                self.taxonomify(desc,id)
                                sequence = ''
                        else:
                                sequence += line.rstrip()
                sequence = self.arbSeqToStr(sequence,skipGapped)
                record = arbSeqRecord( Seq.Seq(sequence,alphabet=generic_rna),id=id, name=name, description=desc)
                yield record

        def taxonomify( self,taxonomy ,accession ):
                """Given the taxonomy in the sequence header (stored as arbSeqRecord.description),
                update the taxonomy dictionary ( self.taxonomy )
                """
                taxonomy = re.split(';',taxonomy)
                if len(taxonomy) > 1:
                        node = self.taxonomy
                else:
                        return ## Hasn't split
                taxLen = len(taxonomy)
                for i in xrange(taxLen):
                        OTU = taxonomy[i]
                        if OTU in node:
                                node = node[OTU]
                        else:
                                node.update( { OTU : {} } )
                        if i == taxLen-1:
                                if 'accessions' in node.keys():
                                        node['accessions'].append(accession)
                                else:
                                        node.update( { 'accessions' : [accession] } )
                return

        def dumpAndIndex( self, outHandle,skipGapped=True,format='fasta'):
                """Writes converted arb sequence file to a file handle.
                Updates the self.index simultaneously.
                """
                index = outHandle.tell()
                for seqRecord in self.parse(self.inFile,skipGapped):
                        outHandle.write(seqRecord.format(format) )
                        self.indexes[seqRecord.id] = index
                        index = outHandle.tell()
		if self.indexFile != None:
			print "Pickling {0} to {1}".format(str(len(self.indexes))+' sequence indexes',self.indexFile.name)
			pickle.dump(self.indexes,self.indexFile,-1)
		else:
			sys.stderr.write( "Sequence index file `{0}` already exists.\n".format( self.inFile.rsplit('.')[0] + '.pklindex'  ) )
			sys.stderr.write( "Leaving as it is. If it's corrupt, first delete and then rerun.\n" )
                self.inFile.close()
                self.inFile = self.outFile

        def pipeSequences(self , accessions ,outPipe):
                """SeqIOIndex - An Index created by IndexDB / SeqIO.index
                accessions - a list of accessions to be returned in fasta
                format"""
		try:
			for accession in accessions:
				if len( accession ) > 0:
					seq = self[accession] #.format('fasta')
					outPipe.send( seq )
		except IndexError,e:
			sys.stderr.write( repr(e) +'\n')
			outPipe.send( 0 )
		finally:
			outPipe.close()
                return
                

def main(options):
    options.options = { '-in': sys.stdin , '-out': sys.stdout  }
    options.parseArgs( sys.argv[1:] )
    ArbIndex = ArbIO( options['-in'] , out = options['-out'] )
    ArbIndex.dumpAndIndex( ArbIndex.outFile )

if __name__ == '__main__':
    from ssummolib import Options
    options = Options()
    main(options)
