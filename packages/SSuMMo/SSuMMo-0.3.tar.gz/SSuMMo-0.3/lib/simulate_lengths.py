#!/usr/bin/env python
"""
Testing ground for passing simulated data through SSUMMO.
This can cut out the V regions using vxtractor, from any
format of input sequences. Can also cut the entire length of 
SSU rRNA, or run do sliding windows of whatever length up
the length of the input sequences.

The full options are quite massive. To see them all, just 
call this file with no arguments.

Examples:-
 1) To cut seqfile.fas from the top down to 30 residues, every 34 resiudes.
       python {filename} -min-length 30 -steps 34 -in seqfile.fas
 2) To cut seqfile.fas using windows 200 bases long.
       python {filename} --windows -window-size 200 -in seqfile.fas
 3) To cut out all 9 V regions at their exact lengths from Archaea RNA sequences.
       python {filename} --regions -in seqfile.fas
 4) To cut out the reverse strand of V regions 3 & 4 from Bacterial sequences.
       python {filename} -regions V3 V4 --reverse -kingdom bacteria -in seqfile.fas

 Required:-
    -in  - <input file>

 Global options:-
    -ncpus [total in computer -1]
    -steps [5] - number of
    -start [root] - start taxon for SSUMMO (path)
    -max-length - maximum length to take from the RNA [either Vregion length or longest sequence].
    -min-length - smallest length of the sequences before stopping SSUMMO [either Vregion length or smallest sequence length].
    '-format' [fasta] - input sequence format.

*****     BE SURE TO SPECIFY -kingdom IF USING --regions / -regions           ********

""".format(  filename = __file__  )

import threading
import time
import os
import sys
import re
import subprocess
import multiprocessing
import CONFIG
from Bio import SeqIO, SeqRecord, Seq, Alphabet
try:
    import SSUMMOv06 as SSUMMO ## needs to be maintained!!
except ImportError:
    raise
    #raise ImportError('Please change line 46 in comparative_results.py to import the correct SSUMMO version!')


def parse_hmmsearch_domtbl(pipe):
    """Given a pipe to hmmsearch domtbl results, will return the results lines
    in a list of lists.
    Example results:-
    #                                                                            --- full sequence --- -------------- this domain -------------   hmm coord   ali cooVrd   env coord
    # target name        accession   tlen query name           accession   qlen   E-value  score  bias   #  of  c-Evalue  i-Evalue  score  bias  from    to  from    to  from    to  acc description of target
    #------------------- ---------- ----- -------------------- ---------- ----- --------- ------ ----- --- --- --------- --------- ------ ----- ----- ----- ----- ----- ----- ----- ---- ---------------------
    lcl|D86414           -           1461 Archaea              -           2998         0 1682.6  65.3   1   1         0         0 1682.5  45.3   634  2012     1  1460     1  1461 1.00 [Metallosphaera hakonensis]
    [   0            1            2      3                    4         5          6    7      8     9  10      11        12     13     14    15    16     17   18    19    20    21   22  ]
    
    """
    reg = re.compile('\s+')
    full_results = []
    for line in pipe.stdout.xreadlines():
        print line.rstrip()
        results = []
        if line.startswith('# '):
            continue
        elif line.startswith('#-'):
            total = 0
            indexes = reg.split(line.rstrip())
            lens = [0]
            for index in indexes:
                lens.append(len(index) + total + 1)
                total += len(index) + 1
#               print line[lens[-2]:lens[-1]]
            del(indexes)
            continue
        else:
            for i in range(1,len(lens)):
                if lens[i] != lens[-1]:
                    results.append(line[lens[i-1]:lens[i]].strip())
#                   print line[lens[i-1]:lens[i]].strip()
                else:
                    results.append(line[lens[i-1]:].strip())
        full_results.append(results)
    return full_results

def hmmsearch_to_domtbl( seq_file_name, path ):
    """Given the a sequence file name and a path to an HMM, this will run hmmsearch
    on them and return a pipe to the domain table.
    """
    key = path[path.rfind('/')+1:]
    if type(seq_file_name) == str:
        seqs = subprocess.Popen(['cat',seq_file_name],shell=False,stdout = subprocess.PIPE ).stdout
        hmmsearch_domtbl = subprocess.Popen( [ os.path.join(CONFIG.hmmerdir,'hmmsearch'),'--domtblout','/dev/stdout','-o',os.devnull,'--noali',os.path.join(path,key+'.hmm'),'-'], shell=False, stdin = seqs, stdout = subprocess.PIPE, stderr = subprocess.PIPE,close_fds=True,bufsize=-1)
    elif type(seq_file_name) == SeqRecord.SeqRecord:
        header = '>'+str(seq_file_name.description)
        seqs = seq_file_name.seq.tostring()
        seq = ''
        for i in range(1+ (len(seq_file_name)/80) ):
            seq += '\n' + seqs[ i * 80 : (i*80) + 80 ]
        seqs = header + seq
        hmmsearch_domtbl = subprocess.Popen( [os.path.join( CONFIG.hmmerdir,'hmmsearch'),'--domtblout','/dev/stdout','-o',os.devnull,'--noali',os.path.join(path,key+'.hmm'),'-'], shell=False, stdin =subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE,bufsize=-1)
        hmmsearch_domtbl.stdin.write( seqs )
        hmmsearch_domtbl.stdin.close()
    elif type(seq_file_name) == dict:  # if given a load of SeqRecords
        hmmsearch_domtbl = subprocess.Popen( [ os.path.join( CONFIG.hmmerdir,'hmmsearch'),'--domtblout','/dev/stdout','-o',os.devnull,'--noali',os.path.join(path,key+'.hmm'),'-'], shell=False, stdin =subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE,bufsize=-1)
        for accession in seq_file_name.keys():
            seqrecord = seq_file_name[accession]
            assert type(seqrecord) == SeqRecord.SeqRecord
            header = '>'+str(accession) + '-consensus'
            seqs = seqrecord.seq.tostring()
            seq = ''
            for i in range(1+ (len(seqs)/80) ):
                seq += '\n' + seqs[ i * 80 : (i*80) + 80 ]
            seqs = header + seq
            hmmsearch_domtbl.stdin.write(seqs)
        hmmsearch_domtbl.stdin.close()
    else:
        sys.stderr.write( "\n# seq_file_name should be a Bio.SeqRecord.SeqRecord, filename as string, or dictionary of { accession : SeqRecord }\n# Got {0} - {1}".format( type(seq_file_name) , seq_file_Name ) )
        raise TypeError
    return hmmsearch_domtbl

def getMinMeanMaxSeqLengths(in_file_name,seq_file_format):
    """This searches through the given file name and returns a tuple
    with the minimum and maximum sequnce lengths in that file"""
    lengths = []
    with file(in_file_name,'r') as inHandle:
        replSub = re.compile( r'([\n\r-])+' )
        for seq in SeqIO.parse( inHandle,seq_file_format):
            lengths.append( len( replSub.sub('', seq.seq.tostring() ) ) )
        N = len( lengths )
    avLen = float(sum(lengths)) / float( N )
    return min(lengths),avLen,max(lengths), N

class Writer():
    replSub = re.compile( r'([\n\r-\.])+' ) # Takes out new lines and insertion / deletions.
    @classmethod
    def writer(cls, seqRecord,length,start=0 ):
        seqRecord.seq = Seq.Seq( cls.replSub.sub( '', seqRecord.seq.tostring() ), alphabet=Alphabet.generic_rna )[start:start+length]
        return seqRecord
    @classmethod
    def reverser(cls, seqRecord,length,start=0 ):
        """N.B. This doesn't take the reverse complement. It returns a
        sequence slice from the opposite end."""
        seqRecord.seq = Seq.Seq( cls.replSub.sub( '', seqRecord.seq.tostring() ) , alphabet = Alphabet.generic_rna )[-start-length:-start]
        #seqRecord = seqRecord[-start-length:-start]
        #seqRecord.seq = seqRecord.seq.reverse_complement()
        return seqRecord

def rewriteSeqsAtLength( options, length, seq_file_format='fasta', start=0, min_length=10 ):
    """Given an Options() object, a maximum sequence length, this will rewrite those sequences to
    options['-out'].
    Optionally, provide a start location. Otherwise it'll cut the sequence from the start up
    until the given length (if the sequence is that long)"""
    if length == None:
        length = 1000000000
    outName = options['-out']
    if '.' in outName and '_CUT' not in outName:
        outName = options['-out'].rsplit('.',1)[0]+'_CUT.fas'
    lengths = []
    tooShort = 0
    with file(options['-in'],'r') as inHandle:
        with file(outName,'w') as outHandle:
            replSub = re.compile( r'([\n\r-\.])+' )  ## Takes out new lines and gaps (- or .).
            if CONFIG.options['--reverse']:
                writer = Writer.reverser
            else:
                writer = Writer.writer
            for seqRecord in SeqIO.parse(inHandle, seq_file_format):
                seqRecord = writer( seqRecord, length, start=start )
                if len( seqRecord ) >= min_length:
                    outHandle.write( writer( seqRecord, length ).format('fasta') )
                    lengths.append( len( seqRecord ) )
                else:
                    tooShort += 1
                continue 
    if lengths == []:
        sys.stderr.write( "No sequences found in {0} are long enough ({1} too short).\n".format(options['-in'],tooShort))
        sys.stderr.flush()
        return 0,0,0,0
    avLen = float( sum(lengths) ) / float( len(lengths) )
    return min(lengths),avLen, max(lengths) , len(lengths )
    
def callSSUMMO( inName, SSUMMO_Options ):
    #options = SSUMMO.LocalOptions()
    args = []
    options = SSUMMO_Options.options
    for opt_key in options:
        if opt_key in ['-in','-out']:
            continue
        if type(options[opt_key]) == list:
            options.update( { opt_key : ' '.join( options[opt_key] ) } )
            args += [ opt_key , options[opt_key] ]
        elif type( options[opt_key] ) == str:
            args += [opt_key, options[opt_key] ]
    args += ['-in',inName]
    out = file(os.devnull,'w')
    x = [ sys.executable , os.path.join( CONFIG.top, 'bin', 'SSUMMOv06.py' ) ] + args# [ ' '.join([ str(x) for x in  opt]) for opt in options.iteritems()]
    process = subprocess.call( x , shell=False , stdout = out, bufsize=1 )
    #proc = threading.Thread( target=SSUMMO.main, args=(options,), name='SSUMMO_thread' )
    #proc.start()
    #proc.join()
    #return

    #x = ['python' , os.path.join( CONFIG.top, 'bin', 'SSUMMOv06.py' ) ] + args# [ ' '.join([ str(x) for x in  opt]) for opt in options.iteritems()]
    #if start != None:
    #   process = subprocess.call( ['python',os.path.join(CONFIG.top,'bin','SSUMMOv06.py'),'-ncpus',str(CONFIG.options['-ncpus']),'-start',start,inName],shell=False,stdout=out,bufsize=-1 )
    #else:
    #   process = subprocess.call( ['python',os.path.join(CONFIG.top,'bin','SSUMMOv06.py'),inName],shell=False,stdout=out,bufsize=-1 )
    retCode = process ## when using .call() 
    if retCode != 0:
        raise IOError
    return

def callTallyDict( inName ):
    process = subprocess.Popen( [sys.executable,os.path.join(CONFIG.top,'bin','SSUMMO_tally.py') ,'--tally','-in',inName],shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE )
    #genus_matches = re.compile( r'(^\d+)\s+.*(at the genus level)' )
    #species_matches = re.compile( r'(^\d+)\s{1}.*(at species level)' )
    genus_matches = re.compile( r'^genus\s+(\d+)[/\s]+(\d+)[\s=]+([\d\.]+)' )   # 3 groups: number matched, number found, %age accuracy
    species_matches = re.compile( r'^species\s+(\d+)[/\s]+(\d+)[\s=]+([\d\.]+)' )  # 3 groups: number matched, number found, %age accuracy
    lines = ''
    n_gen_matched = 0 ; n_spe_matched = 0
    for line in process.stdout:
        genus_match = genus_matches.search( line )        
        species_match = species_matches.search( line )
        #if line.rstrip().endswith('agree at the genus level'):
        if genus_match:
            n_gen_matched, n_gen_found , p_gen = genus_match.groups()
            #nGenus = int( genus_matches.search(line).groups()[0] )
        #elif line.rstrip().endswith('agree at species level'):
        elif species_match:
            n_spe_matched, n_spe_found , p_spe = species_match.groups()
            #nSpecies = int( species_matches.search(line).groups()[0] )
        lines += line
    retcode = process.wait()
    if retcode != 0:
        sys.stderr.write( lines )
        sys.stderr.write( process.stderr.read() )
        raise IOError( "Problem with SSUMMO_tally." )
    process.stderr.close()
    process.stdout.close()
    return int(n_gen_matched), int(n_spe_matched)
    #return nGenus, nSpecies

def getRegion( inFileName,length, Vregion,kingdom='archaea' ):
    print "# Extracting {0} using Vxtractor".format(Vregion)
    prefix = inFileName[: inFileName.rfind('.') ]
    outName = prefix + '_'+Vregion +'.fas'
    null = file( os.devnull,'w')
    if CONFIG.options['-max-length'] == None:
        retCode = subprocess.call( [ os.path.join( CONFIG.VxtractorDir , 'vxtractor.pl') ,'-o',outName,'-h',os.path.join(CONFIG.VxtractorDir,'HMMs',kingdom),'-region',Vregion,inFileName ],shell=False ,stdout=null , stderr=null )
    elif CONFIG.options['--reverse']:
        retCode = subprocess.call( [ os.path.join( CONFIG.VxtractorDir , 'vxtractor.pl') ,'-o',outName,'-h',os.path.join(CONFIG.VxtractorDir,'HMMs',kingdom),'-region',Vregion,'-rlength',str(length),inFileName ],shell=False, stdout=null, stderr=null )
    else:
        retCode = subprocess.call( [ os.path.join( CONFIG.VxtractorDir , 'vxtractor.pl') ,'-o',outName,'-h',os.path.join(CONFIG.VxtractorDir,'HMMs',kingdom),'-region',Vregion,'-length',str(length),inFileName ], shell=False,stdout=null, stderr=null )
    if retCode != 0:
        raise IOError("Vxtractor Broke!!!")
    null.close()
    return outName

class Options():
    """Class to parse command line options."""
    def __init__(self,args=None):
        self.options = { '-start' :     CONFIG.arbDBdir ,
                '-in' :     None ,
                '-out':     None ,
                '-ncpus':   multiprocessing.cpu_count()-1 ,
                '-regions': None,
                '-kingdom': 'archaea',
                '-max-length':  None,
                '-steps' :  5, 
                '-min-length' : None ,
                '-window-size': 250,
                '-format':  'fasta',
                '--windows' :   False ,
                '--reverse':    False,
                '--regions':    False,
                }
        self.helpTxt = { '-in' : 'Input sequence file. Required',
                '-start' : 'Start directory for SSUMMO. By default, SSUMMO will search everything, with first iteration scoring against Bacteria, Archaea & Eukaryota.',
                '-out' : 'Suffix of all the output files. By default, use -in, appending _CUT to the suffix.',
                '-regions' : 'Here you can specify any number of V regions to extract with Vxtractor (up to V9 for Prokaryotes or V8 for Eukaryotes). Use "--regions" for all of them.',
                '-ncpus' : 'Number of processes to allow SSUMMO to use.',
                                '-max-length': 'Maximum length of extracted regions / windows. [Default: go with whatever].',
                '-steps': 'Number of residues to cut each iteration. Default: 5.',
                '-min-length': 'Minimum length of extracted regions / windows. Default: 30.',
                '-window-size' : 'Length of sliding windows. Must supply "--windows" switch. Default: 250.',
                '-format' : 'Sequence format. Default: fasta',
                '-kingdom': 'Domain name to give to Vxtractor. This is the directory name within CONFIG.VxtractorDir/hmms containing the HMMs of interest. Default: archaea.'
                }
        self.switches = {
                '--regions': 'Extract all V regions. Default: False',
                '--windows'  : 'Do sliding windows. Default: False.',
                '--reverse' : "Extract V regions (with Vxtractor) from the 3' end. Default: False."
                }
        self.useage = "\nUseage:-\n  python simulate_lengths.py [options] sequence_file.fas\n"
        self.example = "\nExample:-\n  python simulate_lengths.py -regions V1 V4 V8 -max-length 500 -steps 10 /path/to/test_seqs.fna\n"
        self.singleargs = ['-out','-kingdom','-in','-start','-ncpus','-max-length','-min-length','-format','-window-size','-steps']  ## These options take a single argument.
        self.multiargs =  ['-regions']
        if args != None:
            self.parseArgs( args )
    def printHelp(self):
        """Prints help info for the options defined in self.options"""
        sys.stderr.write( '\nValid options (take argument(s)):-\n' )
        for key,val in self.helpTxt.items():
            sys.stderr.write( '{0}: {1}\n'.format(key.ljust(13),val))
        sys.stderr.write( '\nSwitches (take no arguments):-\n' )
        for key,val in self.switches.items():
            sys.stderr.write( '{0}: {1}\n'.format(key.ljust(13),val))
        sys.stderr.write( self.useage )
        sys.stderr.write( self.example )
        sys.stderr.write( "Received:\n{0}\n".format( ' '.join( self.args ) ) )

    def calc_defaults( self ):
        if self.options['-in'] is not None:
            self.options['-in'] = os.path.realpath( self.options['-in'] )
        else:
            raise IOError( "No input file defined!" )
        min_length, av_length, max_length, nseqs = getMinMeanMaxSeqLengths(self.options['-in'] , self.options['-format'])
        if self.options['-min-length'] is None:
            self.options['-min-length'] = 0
        else:
            self.options['-min-length'] = int( self.options['-min-length'] )

        if self.options['-max-length'] is None:
            self.options['-max-length'] = max_length
        else:
            self.options['-max-length'] = int( self.options['-max-length'] )

        if self.options['-steps']:
            self.options['-steps'] = int( self.options['-steps'] )

        if self.options['-window-size']:
            self.options['-window-size'] = int( self.options['-window-size'] )

        if self.options['-out'] is None:
            inName = str(self.options['-in'])
            name = inName[:inName.rfind('.') + 1]
            self.options['-out'] = name
        return self

    def __getitem__(self,key):
        return self.options[key]
    def __setitem__(self,key,value):
        self.options.update( { key : value } )
        return
    def parseArgs(self,args):
        """Give the command line options and this will update self.options
        and return those updated options as a dictionary."""
        self.args = args
        if len(args) == 0:
            self.printHelp()
            exit()
        prevargDash = False
        for i in xrange(len(args)):
            if args[i].startswith('--'):
                if args[i] in self.options.keys():
                    self.options[ args[i] ] = True
                else:
                    sys.stderr.write( 'Invalid option: {0}\n'.format( args[i] ))
                    self.printHelp()
                    exit()
            elif args[i].startswith('-'):
                if args[i] in self.options.keys():
                    prevargDash = True
                    command = args[i]
                else:
                    sys.stderr.write( 'Invalid option: {0}\n'.format( args[i] ) )
                    self.printHelp()
                    exit()
            elif prevargDash:
                if command in self.singleargs:
                    self.options.update( { command : args[i] } )
                    prevargDash = False
                elif command in self.multiargs:
                    if type( self.options[command] ) == list:
                        self.options[command].append( args[i] )
                    else:
                        self.options.update( { command : [ args[i] ] } )
                else:
                    sys.stderr.write( 'Unrecognised command: {0}\n'.format( command ) )
            else:
                self.options.update( { '-in' : args[i] } )
        return self.options

if __name__ == '__main__':
    t0 = time.time()
    args = sys.argv[1:]
    opt = Options(args)
    opt = opt.calc_defaults()
    ############### END OF SORTING LOCAL OPTIONS ###########
    if '.' in opt['-out']:
        cutSeqName = os.path.realpath( opt['-out'][:opt['-out'].rfind('.')] ) + '_CUT.fas'
    else:
        cutSeqName = os.path.realpath( opt['-out'] + '_CUT.fas' )

    ### CONFIGURING SSUMMO OPTIONS   ###
    CONFIG.options = opt
    ssummoOptions = SSUMMO.LocalOptions()
    defaultOptions = Options()
    for option in CONFIG.options.options:
        if option in ssummoOptions:
            if CONFIG.options[option] != defaultOptions.options[option]:
                ssummoOptions[option] = CONFIG.options[option]  
            else:
                ssummoOptions.options.pop(option)
            
    ssummoOptions.options = { '-in' : ssummoOptions['-in'],
                             '-out' : ssummoOptions['-out'],
                            }
    #################### WINDOWS (not the OS, sequence windows ) #########################
    if opt['--windows']:
        start_location = opt['-max-length'] - opt['-window-size']
        if start_location < (0 or opt['-min-length']) :
            opt['-max-length'] += opt['-window-size']
        start = min( opt['-min-length'] , opt['-max-length'] )
        end = max( opt['-min-length'] , opt['-max-length'] )
        print '# will be analysing sequences with start positions from {0} to {1}, in intervals of {2} with a fixed window size of {3}'.format( start , end , opt['-steps'], opt['-window-size']  )
        print "# That means calling SSUMMO {0} times!!".format(  ( end - start) / opt['-steps'] )
        print ' '.join( [ '# Start Pos'.ljust(12) , 'End Pos'.ljust(8) ,'Nseqs'.ljust(9), 'NGenus:)'.ljust(8),'NSpecies:)'.ljust(8) , '% Genus :)'.ljust(10) ] )
        opt['-out'] = cutSeqName
        for startPos in xrange(  end - 250,  # From the start of each window,
                                 start,                         # to defined min-length [0]
                                 - int(opt['-steps'] )):                     # going back in steps of size opt['-steps']
            minLen, avLen, maxLen, nseqs = rewriteSeqsAtLength( opt, 
                                                                opt['-window-size'], 
                                                                opt['-format'], 
                                                                start = startPos - 250,  # Had this in xrange(), but better here..
                                                                min_length=opt['-window-size'])
            if (minLen, avLen, maxLen, nseqs,) == ( 0,0,0,0,):
                print "## No sequences filling criteria (probably because none are long enough)"
                continue
            print ' '.join( [ str(startPos).ljust(12) , str(startPos + opt['-window-size']).ljust(8),str(nseqs).ljust(9) ] ) ,
            callSSUMMO( cutSeqName ,ssummoOptions)
            nGenus, nSpecies = callTallyDict( cutSeqName )
            print ' '.join( [ str(nGenus).ljust(8), str(nSpecies).ljust(8) , str(100.*nGenus/float(nseqs)).ljust(10) ] )
        t = time.time()
        mins = int(t-t0) / 60
        print "# Successfully finished in {0} mins{1} secs".format( mins, (t - t0) - (mins*60))
        exit()  

    ###################  LOOK AT V REGIONS ####### 
        
    n = range( opt['-max-length']), opt['-min-length'], 0- int(opt['-steps']) 
    print '# will be analysing sequence lengths from {0} to {1} for sequence lengths every {2} residues.'.format( n[0], n[-1],opt['-steps'] )
    if opt['-regions'] != None or opt['--regions']:
        if opt['--regions']:
            doRegions =  ['V{0}'.format(i) for i in range(1,10)]
        else:
            doRegions = []
            for region in opt['-regions']:
                doRegions.append(region)
        print ' '.join( ['# Min length'.ljust(12) , 'Av length'.ljust(9) , 'Max length'.ljust(10) , 'N seqs'.ljust(6) , 'N genus :)'.ljust(10) , 'N species :)'.ljust(12) , '%Genus :)'.ljust(8) ] )
        for i in doRegions:
            outName = getRegion( opt['-in'],opt['-max-length'],'{0}'.format(i), kingdom=opt['-kingdom'])
            minLen,avLen,maxLength,nseqs = getMinMeanMaxSeqLengths( outName , opt['-format'] )
            cutSeqName = os.path.realpath( outName[ : outName.rfind('.') ] + '_CUT.fas' )
            opt['-in'] = cutSeqName
            for maxLen in xrange( maxLength, minLen,0 - int(opt['-steps']) ):
                minLen,avLen,maxLength,nseqs = rewriteSeqsAtLength( opt , maxLen, opt['-format'],min_length=maxLen )
                callSSUMMO( cutSeqName,ssummoOptions )
                nGenus,nSpecies = callTallyDict( cutSeqName )
                pGenus = float(nGenus) / float( nseqs)
                print ' '.join( [ str(minLen).ljust(12) , str(avLen).ljust(9) , str(maxLength).ljust(10) , str(nseqs).ljust(6) , str(nGenus).ljust(10) , str(nSpecies).ljust(12) , str(pGenus).ljust(8) ] )
        exit()
    ################### NO OPTIONS - SLICE FROM END TO START ##############
    else:
        print '# SSUMMO will be called a total of {0} times!!'.format( len(n) )
        print ' '.join( ['# Min length'.ljust(12) , 'Av length'.ljust(9) , 'Max length'.ljust(10) , 'N seqs'.ljust(6) , 'N genus :)'.ljust(10) , 'N species :)'.ljust(12) , '%Genus'.ljust(8) ] )
        for maxLen in xrange( opt['-max-length'], opt['-min-length'], opt['-steps'] ):
            minLen,avLen,maxLength,nseqs = rewriteSeqsAtLength( opt,maxLen, opt['-format'],min_length=maxLen)
            print ' '.join( [ str(minLen).ljust(12) , str(avLen).ljust(9) , str(maxLength).ljust(10) , str(nseqs).ljust(6) ] ) ,
            if opt['-start']!= CONFIG.arbDBdir:
                callSSUMMO(cutSeqName,ssummoOptions) 
            else:
                callSSUMMO( cutSeqName, ssummoOptions )
            nGenus, nSpecies = callTallyDict( cutSeqName )
            pGenus = float(nGenus) / float( nseqs)
            print ' '.join( [ str(nGenus).ljust(10) ,str(nSpecies).ljust(12) , str(pGenus).ljust(8) ] )

    t = time.time()
    mins = int(t-t0) / 60
    print "# Successfully finished in {0} mins{1} secs".format( mins, (t - t0) - (mins*60))
