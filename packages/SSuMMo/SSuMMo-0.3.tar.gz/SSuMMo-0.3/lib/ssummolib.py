#!/usr/bin/env python
"""
General library functions commonly needed for SSUMMO modules.
Not to be called from command line.

"""

import os, sys, re
import cPickle as pickle
import CONFIG
import multiprocessing

try:
    sys.path.append( os.path.join( CONFIG.top, 'bin') )
    from itol import Itol, Dataset
except ImportError:
    sys.stderr.write( "\nCannot find the python Itol library in path. Will stop at creating phyloxml text file\nrather than exporting the tree image\n" )

if __name__ == '__main__':
        sys.stderr.write( 'Do not call directly!' )
        raise IOError

class Options():
        """Class to parse command line options. Overwrite the following options to customise:-

        self.options   - dictionary conataining the data for all options.
        self.helpTxt   - dictionary with help text for all options requiring additional commands.
        self.switches  - dictionary containing help text for all options not requiring commands.
                          All switches start with two dashes '--', and when provided will be changed to have a
                          value of True.
        self.useage    - Show how the program is used (in programmer lingo).
        self.example   - Give an example of how to use it.
        self.singleargs- List containing arguments that can take only one value.
        self.multiarg  - List containing the arguments that can take multiple values (e.g. can often provide multiple input files).
        self.regopts   - list of regular expressions for creating a dynamic number of groups.
                           By default, groups are defined by -groupN where N is any positive integer.
                           Subsequent arguments are file names that are coverged with -in when
                           parseArgs() is called.
        self.post_checks - list of functions which can check the defined arguments after parsing the arguments.
        """
        options = { 
                   '-in' : [] ,
                   '-out': None
                   }
        helpTxt = { '-in' : 'Input sequence file. Required',
                   '-out' : 'Suffix of all the output files. By default, use -in, appending something to the suffix.',
                   }
        switches = {
                   }
        useage = None
        example = None
        singleargs = []
        multiargs  = []
        regargs    = [ re.compile(r'^-group(\d+)') ]
        regopts    = {}
        post_checks = []
        def __init__(self,args=None):
            if sys.platform == 'win32':
                self.post_checks.append( self.expand_stars )
            if args != None:
                self.parseArgs( args )
        def printHelp(self):
            """Prints help info for the options defined in self.options"""
            sys.stderr.write( '\nValid options (take argument(s)):-\n' )
            for key,val in self.helpTxt.items():
                sys.stderr.write( '{0}: {1}\n'.format(key.ljust(15),val))
            if len( self.switches ) > 0:
                sys.stderr.write( '\nSwitches (take no arguments):-\n' )
                for key,val in self.switches.items():
                    sys.stderr.write( '{0}: {1}\n'.format(key.ljust(15),val))
            if self.useage is not None:
                sys.stderr.write( '\nUseage:-\n  ' )
                sys.stderr.write( self.useage + '\n')
            if self.example is not None:
                sys.stderr.write( '\nExample:-\n  ' )
                sys.stderr.write( self.example.rstrip()+'\n' )
        def __getitem__(self,key):
            return self.options[key]
        def __setitem__(self,key,value):
            if key in self.singleargs:
                self.options.update( { key : value } )
            elif key in self.multiargs:
                if type( self.options[key] ) == list:
                    if type( value ) == list:
                        self.options[key] += value
                    else:
                        self.options[key].append(value)
                else:
                    self.options.update( { key : value } )
            else:
                raise KeyError( '{0} is not defined as a singlearg or a multiarg!'.format(key) )
        def __repr__( self ):
            x = ''
            for i in self.options.iteritems():
                x += '{0}:{1}\n'.format( i[0].ljust(20) , str(i[1]).rjust(20) )
            if len( self.regopts ) > 0:
                x += '\nGroup arguments:\n'
                for i in self.regopts.iteritems():
                    x += '{0}:{1}\n'.format( i[0].ljust(20) , str(i[1]).rjust(20) )
            return x
        def parseArgs(self,args):
            """Give the command line options and this will update self.options
            and return those updated options as a dictionary."""
            if len(args) == 0:
                self.printHelp()
                exit()
            prevargDash = False
            for i,arg in enumerate(args):
                if arg.startswith('--'):
                    if arg in self.options:
                        self.options[ arg ] = True
                    else:
                        sys.stderr.write( 'Invalid option: {0}\n'.format( args[i] ))
                        self.printHelp()
                        exit()
                elif arg.startswith('-'):
                    matched = False
                    if arg in self.options:
                        prevargDash = True
                        command = arg
                    else:
                        for regarg in self.regargs:
                            match = regarg.search( arg )
                            if match:
                                prevargDash = True ; matched = True
                                command = arg
                        if not matched:
                            sys.stderr.write( 'Invalid option: {0}'.format( args[i] ) )
                            self.printHelp()
                            exit()
                elif prevargDash:
                    if command in self.multiargs:  ## These options can take multiple args.
                        if type( self.options[command] ) != list:
                            self.options.update( { command : [args[i]] } )
                        else:
                            self.options[command].append(args[i])
                    elif command in self.singleargs:  ## These options take a single argument.
                        self.options.update( { command : arg } )
                        prevargDash = False
                    elif matched:
                        if command in self.regopts:
                            self.regopts[command].append( arg )
                        else:
                            self.regopts.update( { command : [ arg] } )
                    else:
                        sys.stderr.write( 'Unrecognised command: {0}\n'.format( command ) )
                else:
                    if '-in' in self.multiargs:
                        self.options['-in'].append( arg )
                    else:
                        self.options.update( { '-in' : arg } )
            if len( self.regopts ) > 0:
                self.options['_groups'] = []
                self.post_checks.append( self.check_groups )
            for meth in self.post_checks:
                meth()

            return self.options

        def check_groups( self ):
            """Called automatically if any regular expression arguments are defined and
            found when parsing command line options.
            This checks to make sure that there are the same number of grouped files
            as there are input files. If they differ, then this will overwrite files
            provided to -in with files provided in the groups.
            """
            reg_files = self.regopts.values() # list of lists
            self.options['_groups'] = [ len(val) for val in reg_files ]
            n_reg_files = sum( self.options['_groups'] )
            if len(self.options['-in']) < n_reg_files:
                if len( self.options['-in'] ) > 0:
                    sys.stderr.write( 'Number of group files defined differs from the number of input files.\n')
                    sys.stderr.write( 'Taking files defined in groups as -in files.\n' )
                    self.options['-in'] = []
                for group in reg_files:
                    for reg_file in group:
                        if reg_file not in self.options['-in']:
                            self.options['-in'].append( reg_file )
                        else:
                            sys.stderr.write( '{0} defined in -groups at least once already'.format(reg_file) )
            else:
                return

        def _expand_loop(self,path_arg):
            """On windows based machines, there is no shell expansion of 
            stars. This sorts that out!"""
            dirs = self.path_reg.split(path_arg)
            matched = False
            for i,d in enumerate(dirs):
                if '*' in d:
                    pwd = os.path.sep.join( dirs[:i] )
                    files = d.split( '*' )
                    new_reg = re.compile( re.escape( files[0]  ) + 
                              r'.*' + 
                              #r'.*'.format( os.path.sep ) + 
                              re.escape( files[1] ) )
                    for f_name in os.listdir( pwd ):
                        match = new_reg.search( f_name )
                        if match:
                            matched = True
                            yield os.path.join( pwd , match.group() )
            if not matched:
                yield path_arg

        def expand_stars( self ):
            # reg to allow use of cifs shares.
            self.path_reg = re.compile( '(?<=[\w\d\s_\-])[\\/]{1}'  )
            iters = [ self.regopts.items() , self.options.items() ]
            for i,iterator in enumerate(iters):
                for key,value in iterator:
                    if not hasattr( value , '__iter__' ):
                        continue
                    if key in self.singleargs:
                        try:
                            if type( value ) is not (str or int):
                                continue
                            else:
                                value = value[0]
                            matches = [ match for match in self._expand_loop( value ) ]
                        except Exception:
                            print key
                            raise
                        if len(matches) > 1:
                            raise LookupError( "Only one value allowed for {0}. Got more than one match".format( key))
                        elif len(matches) == 0:
                            continue
                        else:
                            if i == 0:
                                self.regopts[key] = matches[0]
                            self.options[key] = matches[0]
                    else:
                        matches = []
                        for val in value:
                            matches += [ match for match in self._expand_loop( val )]
                        if i == 0:
                            self.regopts[key] = matches
                        self.options[key] = matches

class TaxDB:
    def __init__(self):
        import MySQLdb
        self.user = CONFIG.user
        self.host = CONFIG.host
        self.passwd = CONFIG.passwd
        self.db = CONFIG.db
        self.cnx = MySQLdb.connect(user=self.user,host=self.host,passwd=self.passwd,db=self.db)
        self.cur = self.cnx.cursor()
    def FetchTaxID(self,table,OTUName,parentName,Queue=None):
        self.cur.execute('SELECT tax_ID,rank FROM {0} WHERE Name="{1}" AND ParentName="{2}";'.format(  table, OTUName, parentName ))
        IDs = set( (str(r[0]),r[1] ) for r in self.cur.fetchall() )
        if len(IDs) > 1:
            print 'Multiple IDs!!'
            print 'table:\t{0}\nOTU\t{1}\nparent:\t{2}\nID:\t{3}'.format(table,OTUName,parentName,repr(IDs))
            retVal = (0, 'unknown')
        elif len(IDs) == 0:
            self.cur.execute('SELECT tax_ID,rank FROM {0} WHERE Name="{1}";'.format(table,OTUName))
            results = set((str(tax_ID[0]),tax_ID[1]) for tax_ID in self.cur.fetchall() )
            if len(results) == 1:
                retVal = results.pop()
            elif len(results) == 0:
                if ' ' in OTUName:
                    return self.FetchTaxID( table, OTUName.rsplit(' ',1)[0].strip() ,parentName,Queue=Queue )
                retVal = (0, 'unknown')
                pass
            else:
                print "Selecting Name '{0}' from '{1}' gives these results:-\n{2}".format(OTUName,table,results)
                retVal = (0,'unknown')
        else:
            retVal = IDs.pop()
        sys.stdout.flush()
        if Queue is not None:
            Queue.put(retVal)
        else:
            return retVal
    def TaxIDThread(self,inQueue,outPipe):
        x = inQueue.get()
        while x != 'STOP':
            if len(x) == 3:
                table,OTU,parent = x
            else:
                print x
                raise ValueError("Items put into this queue should be of the form (table,OTUname, parentName)")
            outPipe.send( {OTU : self.FetchTaxID(table,OTU,parent,Queue=None) } )
            x = inQueue.get()
    def get_ranks( self , table='Prokaryotes' ):
        self.cur.execute( 'SELECT DISTINCT(Rank) FROM {0};'.format( table ) )
        ranks = [ rank[0] for rank in self.cur.fetchall() ]
        return ranks
    def __del__(self):
            self.cnx.close()

def find_max_depth(node,depth=0,max_depth=0,deepest=[]):
    """Given a node, finds the deepest node and returns it's depth
    and  all nodes of thatdepth"""
    for branch in node.keys():
        if branch == 'accessions':
            continue
        if depth + 1 > max_depth:
            max_depth = depth + 1
            deepest = [branch]
        elif depth + 1 == max_depth:
            deepest.append(branch)
        max_depth, deepest = find_max_depth(node[branch],depth = depth+1,max_depth=max_depth,deepest=deepest)
    return max_depth,deepest

def combine_dicts( results_dicts ):
    """Give a list of SSUMMO results dictionaries. This shall return a
    dictionary containing each & every node from all of those dictionaries.

    Where accessions are found assigned to a node, this will combine the
    accessions from all results_dicts into a list of lists; one list of
    accessions per results dictionary, in the same order as are passed
    to this function."""
    combined_results = {}
    ind = 0
    for results_dict in results_dicts:
        for full_path,results_node in dict_walk( '' , results_dict ):
            if full_path == '':
                continue
            path_list = full_path.split( os.path.sep )
            combined_node = combined_results
            for node_name in path_list:
                if node_name in combined_node.keys():
                    combined_node = combined_node[node_name]
                else:
                    combined_node.update( { node_name : {} } )
                    combined_node = combined_node[node_name]
            if 'accessions' in results_node.keys():
                if 'accessions' in combined_node.keys():
                    combined_node['accessions'][ind] = results_node['accessions']
                else:
                    combined_node.update( { 'accessions' : [ [] for i in xrange( len(results_dicts) ) ] } )
                    combined_node['accessions'][ind] = results_node['accessions']
        ind += 1
    return combined_results


class seqDB( multiprocessing.Process ):
    def __init__(self,seqfile,prefetchQ,outQ,pipes,format='fasta'):
        from ArbIO import ArbIO
        multiprocessing.Process.__init__(self)
        self.prefetchQ = prefetchQ
        self.outQ = outQ
        self.seqfile = file(seqfile,'r')
        self.db = ArbIO(inHandle=self.seqfile,index=True)
        self.outpipes = pipes
    def run(self):
        nseqs = self.db.indexAndInfo()
        inval = self.db.indexes.keys()  ## All accessions
        self.outQ.put( inval )
        while inval != 'END':
            if type( inval ) == list:
                accessions = inval
                sequences = [ seq for seq in self.db.fetch( accessions ) ]
            if type(inval) == int:
                curpipe = self.outpipes[inval][0]
                [curpipe.send(sequence) for sequence in sequences ]
            inval = self.prefetchQ.get()
        self.prefetchQ.close()
    def __del__(self):
        self.seqfile.close()


def findStart(tdict,options):
        """Locates the directory where to enter the SSUMMO loop.
        Default is to start in arbDBdir, which is configured in
        CONFIG.py.
        To change, give the command option '-start /some/path/to/dir'
        """
        if os.path.realpath(options['-start']) == os.path.realpath(CONFIG.arbDBdir):
            return tdict, CONFIG.arbDBdir
        else:
            found = False
            startKeys = tdict.keys()
            if options['-start'].endswith( os.path.sep ):
                appendPathSep = os.path.sep     ## This is used in buildhmms to start with subdirectories of the given path, rather than starting there.
            else:
                appendPathSep = ''
            startDir = options['-start'].rstrip( os.path.sep )
            pathList = startDir.split( os.path.sep)
            for key in startKeys:
                if key in pathList:
                    firstNode = pathList.index(key)
                    break
                else:
                    continue
            node = tdict
            for nodeName in pathList[firstNode:]:
                if nodeName.strip() == '':
                    continue
                else:
                    node = node[nodeName]
                    parentNode = nodeName
            startDir = os.path.join( CONFIG.arbDBdir,os.path.sep.join(pathList[firstNode:]) ) + appendPathSep
            options['-start'] = startDir 
        print "\n##\tStarting SSUMMO from node '{0}' at path '{1}'".format(parentNode, startDir)
        return node, startDir


def reduceToGenus(tdict,TaxDB):
    tables = { 'Eukaryota' : 'Eukaryotes', 'Bacteria' : 'Prokaryotes', 'Archaea':'Prokaryotes' }
    genusList = []
    for domain in tdict.keys():
        if domain not in tables.keys():
            del(tdict[domain])
            continue
        for path,node in dict_walk(domain,tdict[domain]):
            taxList = path.split( os.path.sep )
            if re.search(r'(Bacteria)|(Eukaryota)|(Archaea)',taxList[-1]):
                parentName = 'root'
            else:
                parentName = taxList[-2]
            taxID, rank = TaxDB.FetchTaxID(tables[domain], taxList[-1],parentName )
            if re.search(r'genus',rank,re.I ) and node.keys() != ['accessions']:
                genusList.append(path) 
    for path in genusList[-1:0:-1]:
        node = tdict
        for OTU in path.split( os.path.sep ):
            node = node[OTU]
        accessions = get_accessions( node,accessions=[])
        for key in node.keys():
            del( node[key] )
        node.update( { 'accessions' : accessions } )
    return tdict

def dict_walk(top,taxdict,topdown=True,random=True):
    if not random:
        names = sorted(taxdict.keys())
    else:
        names = taxdict.keys()
    if 'accessions' in names:
        del(names[names.index('accessions')])
    if topdown:
        yield top,taxdict
    for name in names:
        for x in dict_walk(os.path.join(top,name),taxdict[name],topdown=topdown,random=random):
            yield x
    if not topdown:
        yield top,taxdict

def fetchRank(TaxDBObj,table,OTUName,parent_name=None):
        """
        Checks MySQL database for taxon with name OTUName, and
        parent parent_name.
        If a unique rank is found, return that, otherwise return
        False.
        """
        TaxDBObj.cur.execute( 'SELECT Rank,Name from {0} where Name="{1}";'.format(table,OTUName) )
        rank = set( r for r in TaxDBObj.cur.fetchall()  )
        if len(rank) == 1:
            return rank.pop()
        elif len(rank) == 0:
            TaxDBObj.cur.execute( 'SELECT Rank,Name from {0} where Name LIKE "{1}%";'.format(table,OTUName) )
            rank = set( r for r in TaxDBObj.cur.fetchall()  )
            if len(rank) == 1:
                return rank.pop()
            elif len(rank) == 0:
                next_name = OTUName.rsplit( ' ',1 )
                if len( next_name ) == 2:
                    return fetchRank( TaxDBObj, table, next_name[0], parent_name=parent_name )
            else:
                if parent_name is not None:
                    TaxDBObj.cur.execute( 'SELECT Rank, Name from {0} where Name="{1}" and ParentName="{2}";'.format(table, OTUName,parent_name ) )
                    rank = set( r for r in TaxDBObj.cur.fetchall() )
                    if len( rank ) == 1:
                        return rank.pop()
        else:  # more than one rank.
            if parent_name is not None:
                TaxDBObj.cur.execute( 'SELECT Rank, Name from {0} where Name="{1}" and ParentName="{2}";'.format(table, OTUName,parent_name ) )
                rank = set( r for r in TaxDBObj.cur.fetchall() )
                if len( rank ) == 1:
                    return rank.pop()
        return False,False

def getRanks(taxPathList,TaxDBObj):
    """Give a list of all taxonomies you've got, and a TaxDB object.
    This will return a list of all the ranks, mirroring the taxPathList 
    given, and also the table name.
    """
    ranks = ['root']
    taxPath = ','.join(taxPathList)
    domMatch = re.search(r'(Bacteria)|(Eukaryota)|(Archaea)',taxPath,re.I)
    if not domMatch:
        ProRanks = []
        for i in xrange(1, len( taxPathList ) ):
            ProRanks.append( str( TaxDBObj.FetchTaxID( 'Prokaryotes',taxPathList[i], taxPathList[i-1] )[1]   ).lower() )  ## Appending ranks.
        EukRanks = []
        for i in xrange(1, len( taxPathList ) ):
            EukRanks.append( str(TaxDBObj.FetchTaxID( 'Eukaryotes',taxPathList[i], taxPathList[i-1] )[1] ).lower())
        if EukRanks.count( 'unknown') > ProRanks.count( 'unknown' ):
            table = 'Prokaryotes'
            ranks = ProRanks
        else:
            table = 'Eukaryotes'
            ranks = EukRanks
    else:
        if domMatch.groups()[1] is not None:
            table = 'Eukaryotes'
        else:
            table = 'Prokaryotes'
        for i in xrange(1, len( taxPathList ) ):
            ranks.append( str(TaxDBObj.FetchTaxID( table,taxPathList[i], taxPathList[i-1] )[1] ).lower() )
    return ranks, table

class ITOLCGI():
    downloadOptions = { 'fontSize' : 28,
                    'lineWidth' : 1,
                    'showInternalLabels' : 1,
                    'showInternalIDs' : 0,
                    'rangesCover' : 'leaves',
                    'alignLabels' : 1
                    }

    def __init__(self, out_file = None, colour_file = None ):
	self.itol_uploader = Itol.Itol()
        self.ITOLopts = {
                'treeFormat' : 'phyloxml',
                'uploadID' : CONFIG.itolID,
                'projectName' : CONFIG.itolProject,
                'showInternalIDs' : '1',
                } 
        if out_file != None:
            self.ITOLopts.update( { 'treeFile' : out_file.name, 
                'treeDescription' : out_file.name[:out_file.name.rfind('.')],
                } )
        if colour_file != None:
            self.ITOLopts.update( { 'colorDefinitionFile' : colour_file } )
        self.dataset_options = {'Label' : '\%seqs per OTU',
                'Type' : 'multibar',
                'Separator' : 'comma',
                'MultiBarAlign' : '1'
                }
    def add_dataset( self, dataset_file , options='dataset_options' ):
        dataset = Dataset.Dataset()
        dataset.set_dataset_location( dataset_file.name )
        if options == 'dataset_options':
            dataset.add_param_dict( self.dataset_options )
        else:
            dataset.add_param_dict( options )
        self.itol_uploader.add_dataset( dataset )
    def ITOLupload( self ):
        self.XMLname = self.ITOLopts.pop( 'treeFile' )
        self.itol_uploader.set_tree_location( self.XMLname )
        self.itol_uploader.add_upload_param_dict( self.ITOLopts )
        good_upload = self.itol_uploader.upload_tree()
        if not good_upload:
            print 'Error!\n',self.itol_uploader.upload_output()
        webpage = self.itol_uploader.get_webpage()
        print 'Tree Web Page URL:    {0}'.format(webpage)
        return self.itol_uploader

    def ITOLdownload( self, formats=['pdf'] ):
        itol_exporter = self.itol_uploader.get_itol_export()
        graph_name = self.XMLname
        prefix = graph_name[:graph_name.rfind('.')]
        for suffix in formats:
            exportLocation = '{0}.{1}'.format(prefix,suffix)
            itol_exporter.add_export_param_dict( self.downloadOptions )
            itol_exporter.set_export_param_value('format',suffix)
            itol_exporter.set_export_param_value('datasetList','dataset1')
            itol_exporter.export(exportLocation)
            print 'exported {0} formatted tree to {1}.'.format(suffix, exportLocation )

def my_walk(top,taxdict,topdown=True,followlinks=False, random = False):
        """Traverses the dictionary taxdict and yields the full path
        appended to top, and a list of child nodes within the path
        yielded.
        """
        names = taxdict.keys()
        if not random:
                names = sorted( names )
        if 'accessions' in names:
                del( names[names.index('accessions')] )
        if  topdown:
                yield top, names 
        for name in names:
                path   =  os.path.join (top,  name )
                node = taxdict[name]
                for  x  in  my_walk(path, node,  topdown,  followlinks,random ):
                        yield  x
        if  not  topdown:
                yield  top, names


def get_accessions(startNode, accessions = [] ):
    for key in startNode.keys():
        if key == 'accessions':
#                        for accession in startNode[key]:
#                            if accession in accessions:
#                                print accession, startNode.keys()
            accessions += startNode['accessions'] 
        else:
            accessions = get_accessions(startNode[key],accessions=accessions)
    return accessions

def get_combined_accessions(startNode, accessions ):
        for key in startNode.keys():
                if key == 'accessions':
                        for i in xrange(len(startNode['accessions'])):
                                accessions[i] += startNode['accessions'][i]
                else:
                        accessions = get_combined_accessions(startNode[key],accessions)
        return accessions

def find_node_name( target_name , dict_node ):
        start_node = dict_node
        for path, node in dict_walk( '', start_node ):
                if target_name in node.keys():
                        return path
        return None

def find_start_node(resultsDict,taxDict):
        """Locates the directory where to enter the SSUMMO loop.
        Default is to start in arbDBdir, which is configured in
        CONFIG.py.
        To change, give the command option '-start /some/path/to/dir'
        """
        taxNode = taxDict
        result_keys = resultsDict.keys()
        if 'accessions' in result_keys: del( result_keys[ result_keys.index( 'accessions' ) ] )
        for path,node in dict_walk( CONFIG.arbDBdir,taxNode):
            if result_keys[0] in node:
                count = 0
                node_keys = node.keys()
                for key in result_keys:
                    if key in node_keys:
                        count +=1
                if count == len(result_keys):
                    return node,path[len(CONFIG.arbDBdir)+1:]
                else:
                    print 'mismatch between resultsKeys:-\n{0}\n\n and tax keys:-\n{1}'.format( ', '.join( sorted(result_keys) ) , ', '.join( sorted(node_keys) ) )
        sys.stderr.write("\nCan't find the start directory!!\n")
        print result_keys
        print '\n',taxDict.keys()

def load_index(silent=False):
    if not silent:
        sys.stdout.write( 'Loading whole taxonomy index.')
        sys.stdout.flush()
    with file(os.path.join( CONFIG.top , CONFIG.taxIndex) ,'rb') as inFile:
        taxDict = pickle.load(inFile)
    if not silent:
        sys.stdout.write( ' Done.\n' )
    return taxDict



def collapse_at_rank(resultsDict,options,TaxDBObj=None,taxDict=None,combined=False):
        """Collapses a results dictionary at desired rank.
        resultsDict - load (using cPickle.load) a SSUMMO results
            file ( the .pkl file ).
        options - dictionary just needing a key '-collapse-at-rank' with
            the desired rank to collapse as the value.
        TaxDBObj - object of class TaxDB (contained in here, ssummolib.py).
        taxDict - the full taxonomic dictionary index (usually referred to
            by taxIndex in CONFIG.py).
        """
        if TaxDBObj is None:
            TaxDBObj = TaxDB()
        Eukaryota = re.compile( r'Eukaryota' )
        node = resultsDict
        toCollapse = {}
        collapseCount = 0
        collapseRank = re.compile( r'^{0}$'.format( options['-collapse-at-rank'].strip()), re.I )
        if taxDict is not None:
            fullnode,fullPath = find_start_node(node,taxDict)
        else:
            fullPath = os.path.join( CONFIG.arbDBdir , CONFIG.taxIndex )
        sys.stdout.write( 'Collapsing clades at {1} level.'.format(collapseCount,options['-collapse-at-rank'] ) )
        sys.stdout.flush()
        ## First Iteration. Note all the nodes with desired rank.
        for path,node in dict_walk(fullPath,resultsDict):
            pathList = path.split(os.path.sep)
            if len(pathList) > 1:
                parent = pathList[-2]
                if Eukaryota.search( path ):
                    table = 'Eukaryotes'
                else:
                    table = 'Prokaryotes'
            else:
                #null,fullpath = find_start_node( node,fullnode )
                parent = path.split( os.path.sep)[-1]
                table = 'Eukaryotes' if Eukaryota.search(path) else 'Prokaryotes'
            OTU = pathList[-1]
            taxid, nodeRank = TaxDBObj.FetchTaxID( table, OTU,parent )
            if collapseRank.search(nodeRank):
                n = toCollapse  # the node to collapse.
                collapseCount += 1
                for p in pathList:
                    if p in n.keys():
                        n = n[p]
                    else:
                        n.update( {p : {}} )
                        n = n[p]
                n.update( { 'snip' : {} } ) # mark places to cut.
        sys.stdout.write('\nFound {0} clades at {1} level.\nCollapsing... '.format(collapseCount,options['-collapse-at-rank'] ) )
        sys.stdout.flush()
        nCollapsed = 0
        ## Second iteration. Delete any nodes beyond the desired node.
        for path,node in dict_walk(fullPath,toCollapse,topdown=False):
            if 'snip' not in node:
                continue
            realNode = resultsDict
            pathList = path.split( os.path.sep )
            for p in pathList:
                realNode = realNode[p]
            if combined:
                accessions = get_combined_accessions( realNode, accessions = [ [] for i in xrange( len( options['-in'] ) )] )
            else:
                accessions = get_accessions( realNode , accessions=[] )
            for key in realNode.keys():
                del( realNode[key])
            nCollapsed += 1
            realNode.update( { 'accessions' : accessions } )
        sys.stdout.write( ' Collapsed {0} nodes.\n'.format( nCollapsed) )
        return resultsDict


if __name__ == '__main__':
        sys.stderr.write( 'Not to be called directly from command line.\nExiting.\n' )
        exit()
