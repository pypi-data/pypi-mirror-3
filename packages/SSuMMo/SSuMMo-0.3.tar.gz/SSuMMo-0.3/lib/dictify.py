#!/usr/bin/env python
"""
This script looks through a fasta file of SSU... file downloaded from ARB, creating a 
directory hierarchy that reflects the taxonomic ordering as presented by the
ARB data file.
In each of these directories a file ('accessions.txt') is created that contains all the accessions that are descendants of that taxonomic rank.
"""
import ArbIO
import os , sys, re
import time
import subprocess
import CONFIG
import multiprocessing
import threading
import cPickle as pickle
from Bio import SeqIO
from ssummolib import my_walk, dict_walk, findStart, reduceToGenus, TaxDB, get_accessions, Options

def presshmms( tdict ):
    """Traverses tdict, pressing sub-node HMMs into the parent node"""
    prefix = CONFIG.hmmerdir
    builder = HMMBuilder()
    for path, folders in my_walk(CONFIG.arbDBdir, tdict):
        contents = os.listdir(path)
        directory = path[path.rfind( os.path.sep )+1:]
        out_name = dir+'.hmm'
        if folders == []:
            continue
        elif out_name+'.h3m' in contents and out_name+'.h3i' in contents and out_name+'.h3f' in contents and out_name+'.h3p' in contents:
            pass
        path = path.strip()
        if path.endswith('/'):
            path = path[:-1]
        print "pressing {0} dirs in {1}".format(len(folders),path)
        with file( os.path.join(path,'{0}_to_press.hmm'.format(dir)) ,'w') as out_handle:
            for folder in folders:
                temp_path = os.path.join(path,folder)
                builder.buildhmm(temp_path)
                with file( os.path.join(temp_path, folder +'.hmm') ,'r') as in_handle:
                    read = in_handle.read()
                    if read.endswith('\n'):
                        out_handle.write(read)
                    else:
                        out_handle.write(read+'\n')
        subprocess.call( [ os.path.join(prefix,'hmmpress') ,'-f', os.path.join(path, directory+'_to_press.hmm')], shell = False )
        os.remove( os.path.join( path, directory + '_to_press.hmm') )
        for ext in ['h3m','h3i','h3f','h3p']:
            os.rename( os.path.join( path, directory + '_to_press.hmm.'+ext ), os.path.join(path, directory + '.' + ext) )
    return


class SeqDB( multiprocessing.Process) :
    def __init__ (self ):
        multiprocessing.Process.__init__(self)
        self.SeqDBQ = multiprocessing.Queue()
        self.outSeqPipe,self.__inSeqPipe = multiprocessing.Pipe()
    def run(self):
        seqFileName = self.SeqDBQ.get()
        while seqFileName != 'END':
            ArbDB = ArbIO.ArbIO( inHandle= seqFileName, index=True )
            accessions = self.SeqDBQ.get()
            while accessions != 'STOP':
                sequences = [seq for seq in ArbDB.fetch( accessions ) ]
                for sequence in sequences:
                    self.__inSeqPipe.send( sequence )
                accessions = self.SeqDBQ.get()
            ArbDB.close()
            seqFileName = self.SeqDBQ.get()
    def __del__(self):
        self.SeqDBQ.close()
        self.outSeqPipe.close()
        self.__inSeqPipe.close()

class HMMBuilder :
    def __init__(self):
        self.Lock = multiprocessing.RLock()
        self.Q = multiprocessing.Queue()
        self.taxPipe,self.outPipe = multiprocessing.Pipe()
    def __del__(self):
        sys.stdout.flush()
        self.Q.close()
        self.taxPipe.close()
        self.outPipe.close()
    def checkhmm(self, cwd, hmmName, NSeqs ):
        taxid = None
        OTUName = hmmName[:hmmName.rfind('.')]
        if os.path.getsize(os.path.join(cwd, hmmName )) != 0:
            handle = file( os.path.join(cwd, hmmName ),'r')
            top_line = handle.readline()
            out = top_line
#           if 'HMMER2.0' in top_line:
#               os.system('rm -f "{0}/{1}.hmm"'.format(cwd,pwd))
#               contents = os.listdir(cwd)
#               pass
#           else:
#           print '\tAlready done'
            change = False
            countOfSlash = 0
            for line in handle:
                if line.startswith('NAME'):
                    taxid,rank = self.receiveTaxID( self.taxPipe.recv(), OTUName )
                    assigned_name = line[4:].strip()
                    if 'alignment' in assigned_name:
                        line = line.replace('alignment', taxid)
                        change = True
                    elif str(assigned_name) != str(taxid):
                        print "changing name from {0} to {1} in HMM".format(assigned_name,taxid)
                        line = line.replace(assigned_name,taxid)
                        change = True
                elif line.startswith('NSEQS'):
                    HMMnseqs = int(re.split(r'\s',line,1)[1].strip())
                    if HMMnseqs != NSeqs:
                        return True,taxid
                elif line.startswith(''): ## Check alignment length!
                    pass

                elif '//' in line:
                    countOfSlash += 1
                out += line
            handle.close()
            if countOfSlash > 1:
                build = True
                os.remove( os.path.join( cwd, hmmName ))
            elif change == True:
                with file(handle.name,'w') as handle:
                    handle.write(out)
                build=False   ## As doing it again from scratch...
            else:
                build = False
            del(out)
        else:
            build = True
            os.remove( os.path.join(cwd, hmmName) )
        if taxid == None:
            taxid,rank = self.receiveTaxID( self.taxPipe.recv(), OTUName )
        sys.stdout.flush()
        return build,str(taxid),rank
    
    def receiveTaxID(self,TaxNameID,OTUName):
        """TaxNameID is the dictionary sent by pipe from TaxDB.TaxIDThread.
        OTUName is the name of the OTU according to the ARB and the SSUMMO
        database.
        This returns the TaxID if it's unique and the OTU names match.
        If it FetchTaxID returns '0', then this returns the OTU name instead
        of the taxonomic ID."""
        if len( TaxNameID ) == 1 and TaxNameID.keys()[0]== OTUName:
            pass
        else:
            self.Q.put( TaxNameID ) ## Put it back for another process to get.
            TaxNameID = self.taxPipe.recv()
            while TaxNameID.keys()[0] != OTUName:
                self.Q.put( TaxNameID )
                TaxNameID = self.taxPipe.recv()
        x = TaxNameID.values()[0]
        taxid,rank = str(x[0]),x[1]
        if taxid == '0':
            taxid = OTUName
        return taxid,rank

    def buildhmm(self,cwd,nSeqs):
        """
        Checks an HMM given in cwd, returns True if it should be rebuilt, along
        with the NCBI taxonomic identifier and it's rank.
        """
        taxPath = cwd.rstrip( os.path.sep ).split( os.path.sep ) # Split the path into a list
        pwd = taxPath[-1]  ## pwd = last directory name
                                ## cwd = full path
        parentName = taxPath[-2]
        if re.search(r'(Bacteria)|(Eukaryota)|(Archaea)',pwd):
            parentName = 'root'
        hmmName = pwd + '.hmm'
        prefix = CONFIG.hmmerdir
        if 'Archaea' in taxPath:
            table = 'Prokaryotes'
            org = 'arc'
        elif 'Bacteria' in taxPath:
            table = 'Prokaryotes'
            org = 'bac'
        elif 'Eukaryota' in taxPath:
            table = 'Eukaryotes'
            org = 'euk'
        else:
            print "can't determine the kingdom!"
            raise KeyError
        taxid = None
        self.Q.put( [table,pwd,parentName] ) ## For later retrieval of taxID. The other end of this Q is in TaxDB.TaxIDThread
        contents = os.listdir(cwd)
        if hmmName in contents: # If HMM already there, run some checks...
            build,taxid,rank = self.checkhmm(cwd,hmmName,nSeqs)
            return build,str(taxid),rank
        else:
            taxid,rank = self.receiveTaxID( self.taxPipe.recv() , pwd )
            build = True
        return build,taxid,rank

def taxonomic_dictionary(file_handle='', filetype='dir_index'):
    """As input, give a file handle to a fasta file from the ARB.
    This will return a dictionary of dictionaries representing
    all the taxonomic identities of all the contained sequences.

    If using the pickled dictionary file (taxIndex in CONFIG.py),
    please pass it as a read BINARY file handle. (The 'rb')
    e.g.
    with handle as file(taxIndex,'rb'):
            tdict = taxonomic_dictionary(handle)
    """
    folder_hierarchy = {}
    if type(file_handle) == file and filetype != 'fasta':
        print "reading taxonomies from file: {0}".format( file_handle.name )
        if file_handle.name == os.path.join( CONFIG.top, CONFIG.taxIndex):
            return pickle.load(file_handle)
    elif CONFIG.taxIndex in os.listdir(CONFIG.top) and filetype != 'fasta':
        with file(os.path.join( CONFIG.top, CONFIG.taxIndex),'rb') as in_handle:
            print 'Loading ' + in_handle.name
            results_dict = pickle.load(in_handle)
#            if len( results_dict ) < 6:
#                print "{0} is incomplete. Deleting...".format( in_handle.name )
#                os.remove( in_handle.name )
        return results_dict
    if filetype == 'fasta':
        for line in file_handle:
            if line.startswith('>'):
                accession, order = re.split(r'\s+',line[1:].rstrip(),1)
                order = re.sub("(\/)|(['\"])",lambda m: '' if m.groups()[1] else '.',order)
                order = order.split(';')
                node = folder_hierarchy
                for dir in order:
                    if dir == '':
                        continue
                    elif dir not in node:
                        node[dir] = {}
                    node = node[dir]
                if 'accessions' in node.keys():
                    node['accessions'].append(accession)
                else:
                    node.update( { 'accessions' : [accession] } )

            else:
                continue
        with file(os.path.join( CONFIG.top, CONFIG.taxIndex),'wb') as out_handle:
            print 'pickling TaxDict into ',out_handle.name
            pickle.dump(folder_hierarchy,out_handle,-1)
    elif filetype == 'dir_index' or 'file_list' in file_handle.name:
        if file_handle == '':
            raise IOError( 'Please run --indexTaxa first' )
        for line in file_handle:
            order = line.rstrip().split( os.path.sep )
            node = folder_hierarchy
            for dir in order:
                if dir == '':
                    continue
                elif dir not in node:
                    node[dir] = {}
                node = node[dir]
            else:
                continue
        with file(os.path.join(CONFIG.top,CONFIG.taxIndex),'wb') as out_handle:
            pickle.dump(folder_hierarchy,out_handle,-1)
    else:
        raise IOError("Unrecognised index file")
    print "All taxonomies read succesfully."
    return folder_hierarchy

def fasta_to_index_file( in_file ):
    """Reads fasta file into dictionary, outs it to file of directory indexes."""
    tdict = taxonomic_dictionary(file_handle=in_file, filetype='fasta')  ## turns fasta file into dictionary.
    out_file = file('file_list.txt','w')
    top_len = len(CONFIG.arbDBdir) + 1   ## Index for slicing the pathnames to organism name.
    print "traversing {0} according to dictionary {1}".format(CONFIG.arbDBdir, 'node')
    for path, dirs in my_walk('', tdict):
        out_file.write(path+'\n')
    print "saved relative file paths to {0}".format( out_file.name )
    out_file.close()
    return tdict

class hmmbuildProcess( multiprocessing.Process ):
    def __init__( self,semaphore ):
        multiprocessing.Process.__init__(self)
        self.inQueue = multiprocessing.Queue()
        self.inSeqPipe, self.__outSeqs = multiprocessing.Pipe()
        self.sem = semaphore
        self.hmmbuild = os.path.join( CONFIG.hmmerdir, CONFIG.hmmbuildCMD.rsplit(os.path.sep,1)[-1] )
    def run( self ):
        HMMPath,nseqs,taxid = self.inQueue.get()
        while HMMPath != 'STOP':
            buildProcess = subprocess.Popen( [ self.hmmbuild ,'-n',taxid,'--rna','--informat','stockholm', HMMPath, '-' ],shell=False,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=-1)   ## hmmbuild options
            #buildProcess = subprocess.Popen( [ self.hmmbuild ,'-n',taxid,'--iins','--ignorant','--informat','stockholm',HMMPath, '-' ],shell=False,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=-1)    ## infernal options
            SeqIO.write( [ self.__outSeqs.recv() for seqRec in xrange(nseqs)], buildProcess.stdin,'stockholm' )
            buildProcess.stdin.flush()
            buildProcess.stdin.close()
            retCode = buildProcess.wait()
            self.sem.release()
            if retCode != 0:
                sys.stderr.write( "HMMBuild error!" + '\n')
                sys.stderr.write( buildProcess.stderr.read() +'\n')
                sys.stderr.flush()
                null = buildProcess.stdout.read()
            else:
                null = buildProcess.stdout.read(), buildProcess.stderr.read()
                del(null)
            HMMPath,nseqs,taxid = self.inQueue.get()

def buildhmms( path, in_file, tdict,TaxDBObj, SeqDBProcess, node = 'all', threads = None ):
    """Traverse the (indexed) directory hierarchy and runs hmmalign, hmmbuild
    in each of the directories from top onwards."""
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # Sort out the nodes to be traversed.
    dirs = []
    orgs = ['Bacteria','Archaea','Eukaryota']
    print 'Initiating sequence databases'
    if node == 'all':
        if path.endswith(os.path.sep):
            print "Starting with the subdirectories of {0}".format(path)
            for key in tdict.keys():
                dirs.append( os.path.join( path,key ) )
        elif not re.search(r'(Bacteria)|(Eukaryota)|(Archaea)',path):
            for folder in tdict.keys():
                dirs.append( os.path.join( path , folder ))
        else:
            dirs = [path]
            pass
    elif node in tdict.keys():
        dirs = [os.path.join(path,node)]
    else:
        print "%s is not a recognised node. Available nodes are: 'Bacteria', 'Archaea' & 'Eukaryota'" % node
        raise KeyError
    if len(dirs) == 0:
        dirs.append(path)
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    print "Traversing these {0} directories:\n{1}".format(len(dirs),'\n'.join(dirs))
    for folder in dirs:
        try:
            domain = re.search(r'(Bacteria)|(Eukaryota)|(Archaea)',folder).group()
        except AttributeError:
            print "Can't find the domain from the start dir: {0}".format(folder)
            continue
        Builder = HMMBuilder( )
        SeqDBProcess.SeqDBQ.put( os.path.join(CONFIG.top, domain + 'noGaps.fas') )      #### LET THE SEQ. DB PROCESS KNOW THE FILE LOCATION FOR READING.
        taxIDThread = threading.Thread(group=None, target=TaxDBObj.TaxIDThread, name=None, args=(Builder.Q, Builder.outPipe), kwargs=None, verbose=None)
        taxIDThread.start()
        print "Building HMMs within {0} domain".format(folder)
        got = set()
        threadIndexes = {}
        threadInd = -1
        looped = 0
        org = folder[folder.rfind('/')+1:]
        node = tdict
        if org in tdict.keys():
            node = tdict[org]
        ignoreList = []
        for temp_path, taxNode in dict_walk(folder, node, random=True):
            org = temp_path[temp_path.rfind( os.path.sep )+1: ]
            accessions = get_accessions(taxNode,accessions=[])
            nseqs = len(accessions)
            fullHmmName = os.path.join( temp_path, org +'.hmm')
            if not os.path.exists( temp_path ):
                os.makedirs(temp_path)
            if os.path.exists( os.path.join(temp_path,'lock.file')):
                continue
            try:
                x = file( os.path.join(temp_path,'lock.file'),'w')
                x.close()
                tobuild,taxid,rank = Builder.buildhmm(temp_path,nseqs)
#               if re.search(r'genus',rank,re.I):
#                   ignoreList.append(r'({0})'.format(temp_path) )
#                   if len(ignoreList) > 50:
#                       del(ignoreList[:10] )
#                   ignoreReg = '|'.join(ignoreList)
                if tobuild:
                    SeqDBProcess.SeqDBQ.put(accessions)
                    if threadInd >= len(threads) -1:
                        threadInd = 0
                        looped += 1
                    else:
                        threadInd += 1
                    Builder.Lock.acquire()
                    print 'Submitting hmmbuild job with {0} accessions to {1}'.format(nseqs,temp_path)
                    sys.stdout.flush()
                    Builder.Lock.release()
                    threads[threadInd].sem.acquire()
                    threads[threadInd].inQueue.put( [fullHmmName,nseqs,taxid] ) 
                    for N in xrange(nseqs):
                        threads[threadInd].inSeqPipe.send( SeqDBProcess.outSeqPipe.recv() )
            except Exception:
                raise
            finally:
                os.remove( os.path.join( temp_path,'lock.file'))
        Builder.Q.put('STOP')
        SeqDBProcess.SeqDBQ.put('STOP')
        taxIDThread.join()
        del(Builder)
    for job in threads:
        job.inQueue.put(['STOP',None,None])
        job.join()
    SeqDBProcess.SeqDBQ.put('END')

def hmm_checker( in_file, options = {'-start' : CONFIG.arbDBdir} ):
    """Walks all directories and prints out the number of sequences.
    top = full path to root directory containing Archaea, Bacteria
        & Eukaryota phylogenies.
    in_file = handle for file containing index of subdirectories.
    node = Taxonomic Domain(s) of interest

    e.g.
    from dictify import hmm_checker
    index_handle = file('file_list.txt','r')
    hmm_checker('/path/to/arbDB', index_handle, node=['Bacteria', 'Archaea'])

    This same command can be run directly from the command line with:-
    python dictify.py check Bacteria Archaea
    
    N.B. The '/path/to/arbDB' has to be set correctly in dictify.py before
    this can be called from the command line.
    """
    from count_hmms import countseqs
    top_len = len( options['-start'] )
    done_hmm_count = 0
    misplaced_hmm_count = 0
    done_misplaced_count = 0
    ndirs = 0
    tot_seqs = 0
    nseqs_left = 0
    nleaves = 0
    tax_dict = taxonomic_dictionary( in_file , 'dir_index')
    node, startDir = findStart(tax_dict,options)
    if node == 'all':
        node = tax_dict
    elif node == 'Bacteria':
        node = tax_dict[node]
        top = os.path.join(CONFIG.arbDBdir, 'Bacteria')
    elif node == 'Archaea':
        node = tax_dict[node]
        top = os.path.join(CONFIG.arbDBdir, 'Archaea')
    elif node == 'Eukaryota':
        node = tax_dict[node]
        top = os.path.join(CONFIG.arbDBdir, 'Eukaryota')
    for path, names in my_walk( top, node, random= False ):
        if len(names) == 0:
            nleaves += 1
        cwd = path[path.rfind('/')+1:]
        hmmName = cwd + '.hmm'
        nseqs = countseqs(path)
        done = 0
        try:
            right_place_size = os.path.getsize( os.path.join(path,hmmName) )
            if right_place_size > 0:
                done_hmm_count += 1
                done = 1
        except OSError:
            print "Can't find {0}".format( os.path.join(path, cwd) )
            pass
        try:
            wrong_place_size = os.path.getsize( path + '.hmm' )
            if wrong_place_size > 0:
                misplaced_hmm_count += 1
                if done == 0:
                    done_misplaced_count += 1
                    print 'misplaced hmm in {0}'.format( path )
                    print 'But we already have it in the correct place...'
                    os.rename( path + '.hmm' , os.path.join(path,hmmName) )
            else:
                os.remove( path + '.hmm' )
        except OSError:
            pass
        if done == 0:
            nseqs_left += nseqs
        tot_seqs += nseqs
        ndirs += 1
    try:
        print '%s out of %s sequences processed. %0d%% complete.' % (str(tot_seqs - nseqs_left), str(tot_seqs), 100 * (float(tot_seqs - nseqs_left)/tot_seqs))
    except ZeroDivisionError:
        print "didn't traverse directories properly"
    nhmmsleft = ndirs - done_hmm_count - done_misplaced_count
    print "Number of hmms still to build:\t%s" % str(nhmmsleft)
    print 'Total number of directories:  \t%s' % str(ndirs)
    print 'Number of hmms done right:    \t%s' % str(done_hmm_count)
    print 'number misplaced hmms:        \t%s' % str(misplaced_hmm_count)
    print 'number done in wrong place, but not right place\t%s' % str(done_misplaced_count)
    print "Number of leaves:             \t%s" % str(nleaves)
    return nseqs_left, nhmmsleft


def getSequences(ArbIOobj , accessions ,outPipe):
    """SeqIOIndex - An Index created by IndexDB / SeqIO.index
    accessions - a list of accessions to be returned in fasta
    format"""
    for accession in accessions:
        if len( accession) > 0:
            seq = ArbIOobj[accession].format('fasta')
            outPipe.send( seq )
    outPipe.close()
    return

def splitTaxa( SeqFile ):
    childPipe, parentPipe = multiprocessing.Pipe()
    tdict = taxonomic_dictionary()
    keys = tdict.keys()
    accDict = {}
    for key in keys:
        node = tdict[key]
        accDict.update( { key : get_accessions(node ,accessions=[]) } )
    inHandle = file( SeqFile,'r' )
    print 'keys',accDict.keys()
    ArbDB = ArbIO.ArbIO( inHandle=SeqFile, index=True)
    for kingdom, accessions in accDict.items():
        print 'getting',len(accessions),'sequences from',kingdom
        seqproc = multiprocessing.Process(target=ArbDB.pipeSequences,args=(accessions,childPipe))
        seqproc.start()
        with file( os.path.join(CONFIG.top, kingdom + '.fas') ,'w') as kingfile:
            sys.stdout.write( 'Saving {0} sequences to {1}.\n'.format( kingdom , kingfile.name ) )
            for i in xrange(len(accessions)):
                seqRec = parentPipe.recv()
                try:
                    kingfile.write( '>'+seqRec.id+'\n' )
                    seq = seqRec.seq.tostring()
                except AttributeError, e:
                    sys.stderr.write( 'Problem with ArbIO.ArbIO\n' )
                    break
                #for ind in xrange( (len( seqRec )/80) + 1) :
                for ind in xrange( 0 , len( seqRec ) + 80 , 80 ) :
                #    ind *= 80
                    kingfile.write(seq[ind : 80 + ind]+'\n')
        seqproc.join()
    if not inHandle.closed:
        inHandle.close()

def deleteNonUniques(tdict, tDB):
    tDB.cur.execute('SELECT * FROM NonUniques;')
    NonUniqueRows = tDB.cur.fetchall()
    tDB.cnx.close()
    NonUniques = set()
    names = set()
    for row in NonUniqueRows:
        root,name,parentName = row[:3]
        node = tdict
        print 'Looking for ',name,'with type: ',type(name) 
        for path,dirs in my_walk('',node):
            if name in path:
                print path
        NonUniques.add( (root,name,parentName) )
        names.add(name)
        print (root,name,parentName)
    exit()
    print "We have {0} non-unique nodes to start with".format(len(NonUniques))
    print 'names:',names
    print 'uncultured Xanthomonas sp.' in names
    count = 0
    deletedAccessions = []
    counter = 0
    tot = 0
    for path, dirs in my_walk( '', tdict ):
        tot += 1
        pathList = path.rstrip().split( os.path.sep )
        root = pathList[0]
        Name = pathList[-1]
        if root == Name:
            parentName = 'root'
        else:
            parentName = pathList[-2]
        if Name in names:
            print 'found',Name,'with parentName:',parentName
            if (root,Name,parentName) in NonUniques:
                print 'Found ' + str((root,Name,parentName))
            else:
                print "Didn't find",root,Name,parentName
            count += 1
            node = tdict
            for Dir in pathList[:-1]:
                node = node[Dir]
            deletedAccessions += get_accessions(node[pathList[-1]] )
            del(node[pathList[-1]])
        else:
            for row in NonUniques:
                if Name == row[1]:
                    print 'found: ',str( (root,Name,parentName))
        if counter > 100 and counter < 150:
            print 'counter-range: ',(root,Name,parentName)
        counter += 1
    print "Deleted {0} accession numbers from {1} OTUs".format(len(deletedAccessions), count )
    print "Traversed {0} OTUs".format(tot)
    return deletedAccessions, tdict

def gapbgone( files,threshold='100' ):
    for node in files:
        if os.path.exists(node):
            fileName = node
        else:
            fileName = node+'.fas'
            try:
                assert os.path.exists(fileName)
            except AssertionError:
                print "Can't find",fileName
                raise AssertionError("Make sure you've run 'python dictify.py --splitTaxa <filename>' first.")
        backupFile = fileName + '.bak' 
        print "Backing up {0} to {1}".format( fileName , backupFile )
        os.rename( fileName , backupFile )
        print "Running gapbgone.pl on {0}. Resaving to {1}".format(backupFile,fileName)
        with file(fileName,'w') as outHandle:
            GapGo = subprocess.Popen( [os.path.join( CONFIG.top,'bin','gapbgone.pl'),'-p',str(threshold),backupFile],shell=False,stdout = outHandle,stderr = subprocess.PIPE )
            retCode = GapGo.wait()
            if retCode != 0:
                print GapGo.stderr.read()
        prefix = fileName[:fileName.rfind('.')]
        if os.path.exists( prefix + '.pklindex' ):
            os.remove( prefix + '.pklindex' )
        IO = ArbIO.ArbIO( fileName, index=True)
        IO.index()
        IO.close()

def IIndexTaxa( options ):
    try:
        in_file_name = options['-in']
    except IndexError:
        raise IndexError("Provide a fasta sequence file with taxonomies in the headers please!")
    if in_file_name.strip()=='':
        raise IndexError("Provide a fasta sequence file with taxonomies in the headers please!")
    with file(in_file_name,'r') as in_file: 
        fasta_to_index_file( in_file )
    print "Taxonomy Index file '{0}' has been created.".format(CONFIG.taxIndex)
    return 0

def IRewrite( options ):
    """This rewrites all ARB sequences to a file in a specified format.
    This'll also dump a byte-index of the output sequences to the same
    name as the output file. This causes problems if writing to standard
    out, as won't have write permission to save to /dev/stdout.pklindex,
    so will then save byte index to the name of the input file(.pklindex).
    """
    inSeqFile = options['-in']
    outSeqFile = options['-out']
    if type(outSeqFile) == file and outSeqFile != sys.stdout:
        prefix = outSeqFile.name.rsplit('.',1)[0]
    elif outSeqFile == sys.stdout:
        prefix = options['-in'].rsplit('.',1)[0]
    else:   # Assume outSeqFile is a pathname. We strip the extension and add `.fas` anyway.
        prefix = outSeqFile[:outSeqFile.rfind('.')]
    if not os.path.exists(inSeqFile):
        print "{0} doesn't exist. Make sure you reference either a fasta sequence or an ARB sequence file\nExiting...".format( inSeqFile )
        exit()
    outName = prefix + '.fas'
    IO = ArbIO.ArbIO( inHandle=inSeqFile, out=outName,index=True)
    IO.dumpAndIndex( IO.outFile )
    print 'Saved an index of the arb sequence file: {0}.\nPlease keep in the same directory as the sequence file'.format( prefix + '.pklindex')
    IO.close()
    return 0

def IIndexSeqs( options ):
    inSeqFile = options['-in']
    prefix = inSeqFile[:inSeqFile.rfind('.')]
    if os.path.exists( prefix + '.pklindex' ):
        os.remove( prefix + '.pklindex' )
    IO = ArbIO.ArbIO( inSeqFile, index=True)
    index = IO.index()
    with file( prefix + '.pklindex','wb') as outIndex:
        pickle.dump(index,outIndex,-1)
    return 0

def IDeleteNonUniques( options ):
    with file( os.path.join( CONFIG.top, CONFIG.taxIndex ), 'rb') as infile:
        tdict = pickle.load(infile)
    print 'Deleting NonUnique OTU names from the taxonomy database'
    TaxDBObj = TaxDB()
    deletedAccessions, tdict = deleteNonUniques( tdict , TaxDBObj)
    inFile =  file(options['-in'],'r')
    ArbIOObj = ArbIO.ArbIO(inFile, index=True)
    childPipe, parentPipe = multiprocessing.Pipe()
    seqProc = multiprocessing.Process(target=ArbIOObj.pipeSequences,args=(deletedAccessions, childPipe) )
    seqProc.start()
    with file( os.path.join( CONFIG.top,'NonUniqueOTUNameSeqs.fas'),'w') as outFile:
        print 'Saving sequences assigned to Non Unique OTU names to NonUniqueOTUNameSeqs.fas'
        for seq in range(len(deletedAccessions)):
            outFile.write( parentPipe.recv() )
    seqProc.join()
    return 0

def ISplitTaxa( options ):
    inSeqFile = options['-in']
    if options['-out'] != sys.stdout:
        print "No single output file here. Creating Bacteria.fas, Archaea.fas, Eukaryota.fas and associated .fasindex files"
    splitTaxa(inSeqFile)
    return 0

def IGapBGone( options ):
    if options['-in'] == '':
        with file( os.path.join( CONFIG.top, CONFIG.taxIndex) , 'rb') as inhandle:
            tdict = pickle.load(inhandle)
        keys = tdict.keys()
        del(tdict)
    else:
        keys = [options['-in']]
    gapbgone(keys,options['-gapThreshold'])
    return 0

def IBuildHmms( options ):
    SeqDBProc = SeqDB(  )
    SeqDBProc.start()
    semaphore = multiprocessing.Semaphore( options['-ncpus'])
    print "Submitting hmmbuild jobs across {0} processors".format(options['-ncpus'])
    workers = [ hmmbuildProcess( semaphore ) for i in xrange(options['-ncpus']) ]
    for i in xrange( options['-ncpus'] ):
        workers[i].start()
    with file( os.path.join( CONFIG.top, CONFIG.taxIndex),'rb') as taxIndFile:
        tdict = taxonomic_dictionary( taxIndFile, 'dir_index' )
    TaxDBObj = TaxDB()
    node, startDir = findStart(tdict,options)
    buildhmms( startDir , options['-in'], node, TaxDBObj,SeqDBProc,threads = workers)
    SeqDBProc.join()
    return 0

def ICheck( options ):
    seqs_left, hmms_left = hmm_checker( os.path.join( CONFIG.top , CONFIG.taxIndex) , options = options)
    print "%s sequences left to do" % seqs_left
    print "%s hmms left to build" % hmms_left
    return 0

def IPressHmms( options ):
    in_file = options['-in']
    with file( os.path.join( CONFIG.top , CONFIG.taxIndex),'rb') as input_file:
        tdict = taxonomic_dictionary( in_file )
    for key in tdict.keys():
        if key != 'Bacteria' and key != 'Archaea' and key != 'Eukaryota':
            del(tdict[key])
    presshmms(CONFIG.arbDBdir,tdict)
    return 0


def IReduceToGenus( options ):
    with file( os.path.join( CONFIG.top , CONFIG.taxIndex ),'rb') as inFile:
        tdict = pickle.load(inFile)
    taxDBObj = TaxDB()
    startCounter = 0
    for path,node in dict_walk('',tdict ):
        startCounter += 1
    print 'Starting with {0} nodes'.format(startCounter)
    outDict = reduceToGenus(tdict,taxDBObj)
    endCounter = 0
    for path,node in dict_walk('',tdict ):
        endCounter += 1
    print 'Deleted {0} nodes to end with {1} nodes'.format(startCounter-endCounter,endCounter)
    outIndex = CONFIG.taxIndex[:CONFIG.taxIndex.rfind('.')] + '_toGenus.pkl'
    with file( os.path.join( CONFIG.top , outIndex ),'wb') as outFile:
        pickle.dump( outDict, outFile,-1 )
    return 0

def IRemoveAccessions( options ):
    with file( os.path.join( CONFIG.top , CONFIG.taxIndex ),'rb') as inFile:
        tdict = pickle.load( inFile )
    for path, node in dict_walk('',tdict):
        if 'accessions' in node:
            del( node['accessions'] )
    prefix,suffix = CONFIG.taxIndex.rsplit('.',1)
    digit = re.search( r'^(.*)(\d+)$', prefix )
    if digit:
        prefix = digit.groups()[0] + str( int(digit.groups()[1])+1)
    else:
        prefix = prefix + '1'
    save = '.'.join([prefix,suffix])
    with file( os.path.join( CONFIG.top , save ) ,'rb') as outFile:
        pickle.dump( tdict , outFile,-1 )
    print 'Saved Bare taxonomic structure to {0}'.format( outFile.name )
    return 0
    
def IProcessOptions( options ):
    ######     First step. Build the taxonomy from sequence headers.
    if options['--indexTaxa']:
        IIndexTaxa( options )
    ###### Make sure you do this at least once... From then on, refer to the 
    ###### the outfile you specified.
    if options['--rewrite']: # Resave ARB alignment to <out> 
        IRewrite( options )
    ########### Next. Index Sequence locations in the arb file.
    if options['--indexSeqs']:
        IIndexSeqs( options )
    ########## Optional, but recommended. Delete Clade names which are presented in the
    ########## ARB taxonomy multiple times.
    if options['--deleteNonUniques']:
        IDeleteNonUniques( options )
    ########## Split the ARB sequence database into separate files, one per kingdom.
    elif options['--splitTaxa']:
        ISplitTaxa( options )
    if options['--gapbgone']:
        IGapBGone( options )
    ########## Third step #########
    elif options['--buildhmms']:
        IBuildHmms( options )
    ############# Anytime ##############
    elif options['--check']:
        ICheck( options )
    elif options['--reduceToGenus']:
        IReduceToGenus( options )
    ############# Further development stopped due to being slower ########
    elif options['--presshmms']:
        IPressHmms( options )
    else:
        pass

class MyOptions( Options ):
    def __init__(self,*args):
        Options.__init__(self,*args)
        self.options = { # defaults.
            '-in':'' , 
            '-out': sys.stdout ,
            '-gapThreshold' : 100 ,
            '-ncpus':multiprocessing.cpu_count()-1,
            '-start' : CONFIG.arbDBdir
           }  
        self.singleargs = ['-in','-out','-gapThreshold','-ncpus','-start']
        self.commands = {
            '--indexTaxa' :     False,
            '--deleteNonUniques':   False,
            '--indexSeqs':      False,
            '--splitTaxa':      False,
            '--blast' :         False, 
            '--buildhmms' :     False, 
            '--check' :         False, 
            '--presshmms':      False, 
            '--rewrite' :       False, 
            '--gapbgone':       False, 
            '--reduceToGenus':  False,
            '--removeAccessions':   False,
           }
        self.options.update( self.commands )
        self.switches = {
            '--indexTaxa' :     'Creates a binary (pickled) index file for fast indexing of the latest ARB taxononmy, as parsed from their `_tax_` sequence file.',
            '--deleteNonUniques':   'Deletes taxa in the database that are NonUnique.',
            '--indexSeqs':      'Indexes the byte location of every sequence in the ARB sequence / alignment file, to speed searching with a reduced memory footprint.',
            '--splitTaxa':      'Splits the downloaded arbDB sequence alignment file according to taxa found in the pickled index file. Must be run after `--indexTaxa` and before `--removeAccessions`.',
            '--blast' :         'Deprecated, so probably won\'t work, but should be fairly easy to bring back to life.',
            '--buildhmms' :     'Builds all HMMs from directory `arbDB`, specified in CONFIG.py',
            '--check' :         'Checks the status and integrity of HMM database.', 
            '--presshmms':      'Further development stopped due to being slower.',
            '--rewrite' :       'Rewrites an ARB sequence file, also dumping a byte index of each sequence location. Rewriting involves changing `.` chars for `-` at the start & end of each sequence, and also discarding sequences with gaps (`.`) in the middle.', 
            '--gapbgone':       'Removes columns which are gaps in every sequence. Thanks to Bill Hartmann & his lab for the gapbgone perl script.', 
            '--reduceToGenus':  'Reduces the taxonomic dictionary to genus specificity (i.e. deletes species, subspecies etc.).',
            '--removeAccessions':   'Removes accessions from the database index (referenced in CONFIG.py as taxIndex), saving minimised object to new file.',
            }
        self.order = ['--indexTaxa','--rewrite','--indexSeqs','--splitTaxa','--gapbgone','--buildhmms' ] 
        self.useage = 'python dictify.py [COMMAND] [OPTIONS]'
    def printHelp( self ):
        sys.stderr.write( 'Useage:-\n{0}'.format( self.useage ) )
        sys.stderr.write( '\n\nTHESE COMMANDS SHOULD BE CALLED IN THE FOLLOWING ORDER:\n\n' )
        for line in self._OrderedList(self.order):
            sys.stderr.write( line )
        otherOptions = []
        ## Get the rest of the options.
        opts = self.switches.copy()
        opts.update( self.helpTxt )
        for opt in opts:
            if opt not in self.order:
                otherOptions.append( opt )
        for line in self._UnorderedList(otherOptions):
            sys.stderr.write( line )

    def _OrderedList(self,order):
        leftBuf = max( [ len(key) for key in order ] ) + 5
        for i,item in enumerate(order):
            helpText = self.switches[ item ]
            multiline = len(helpText)>80
            if multiline:
                sys.stderr.write( '{0}. {1}'.format(i+1,item).ljust(leftBuf) + helpText[:80] + '\n' )
                for text_ind in xrange(1, 1+(len( helpText )/80) ):
                    yield '{0}{1}\n'.format(' '.ljust(leftBuf), helpText[ text_ind*80 : (1+text_ind)*80 ])
            else:
                yield '{0}{1}\n'.format( '{0}. {1}'.format(i+1,item).ljust(leftBuf),helpText) 
        yield '\n\n{0}\n\nOTHER OPTIONS\n\n'.format( '-'*80)

    def _UnorderedList( self,keys ):
        leftBuf = max( [ len(opt) for opt in keys ] ) + 4
        #sys.stderr.write( switch + self.switches[switch] )
        for key in sorted( keys ):
            if key in self.switches:
                helpText = self.switches[ key ]
            else:
                helpText = self.helpTxt[ key ]
            multiline = len(helpText)>80
            if multiline:
                sys.stderr.write( key.ljust(leftBuf) + helpText[:80] + '\n' )
                for text_ind in xrange(1, 1+(len( helpText )/80) ):
                    yield '{0}{1}\n'.format(' '.ljust(leftBuf), helpText[ text_ind*80 : (1+text_ind)*80 ])
            else:
                yield '{0}{1}\n'.format(key.ljust(leftBuf),helpText) 


    def customBrokenparseArgs( self, args ):
        if len(args) == 0:
            self.printHelp() # This then won't enter the loop (len == 0)
        prevArgDash = False
        for i in range( len(args) ):
            value = args[i]
            if value in self.commands:
                self.options[value] = True
                continue
            if value.startswith('-'):
                if 'help' in value or value == ('-h' or '-H'):
                    self.printHelp()
                    exit()
                if prevArgDash == False:
                    prevArgDash = True
                else:
                    self.options.update( { args[i-1] : True } )
            elif prevArgDash == True:
                command = args[i-1]
                try:
                    assert command in self.options
                except AssertionError,e:
                    self.printHelp()
                    raise AssertionError('Not a valid keyword option: "{0}"'.format(args[i-1]) )
                self.options[command] = value
                prevArgDash = False
            elif len(args) >= 2 and value == args[-2] and os.path.exists(value):
                self.options['-in'] = value
            elif self.options['-in'] == '' and value == args[-1]:
                self.options['-in'] = value
            elif value == args[-1]:
                self.options['-out'] = value
            else:
                self.printHelp()
                #raise IOError("Input arguments not recognised properly. Looking at {0}".format(value))

if __name__ == '__main__':
    #start timer
    t0 = time.time()

    #get command line arguments.
    args = sys.argv[1:]
    options = MyOptions()

    #overwrite default options with command line args
    options.parseArgs( args )

    #do the processing
    IProcessOptions( options )

    #end timer.
    tf = time.time()
    mins = (tf - t0 )/ 60
    hours = int(mins / 60)
    mins_left = mins - (hours * 60)
    print "Took a total of %shrs%.2fmins to complete" % (str(hours), mins_left)
    print "Exiting..."


