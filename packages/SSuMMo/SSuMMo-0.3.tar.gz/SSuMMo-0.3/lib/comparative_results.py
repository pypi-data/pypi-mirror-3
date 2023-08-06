#!/usr/bin/env python
"""
Provide a set of SSUMMO results files (.pkl format) and this will combine the results
into a single phyloxml formatted tree and an ITOL compatible text file that is used
to display multi-valued bar charts showing the abundance of each member at each observed
rank.

Useage:-
python comparative_results.py [options] results1.pkl results2.pkl [results3.pkl] [...]

Options:-

"""
from ssummo.ssummolib import dict_walk, TaxDB, get_combined_accessions, collapse_at_rank,load_index, ITOLCGI, Options , combine_dicts
from ssummo.dict_to_phyloxml import make_colours , colour_node
from itol import Itol, Dataset
import cPickle as pickle
import sys
import os
import colours
import re

class LocalOptions( Options ):
    """Class to parse command line options."""
    def __init__(self,args=None):
        self.options = {
                     '-out' : None,
                     '-out-graph': None,
                     '-out-heatmap':None,
                     '-collapse-at-rank':False,
                     '-in':[],
                     '--upload' : False,
                     '--download' : False,
                     '-out-formats' : [],
                     '-unknowns': None,
                }
        self.helpTxt = {
                    '-out' : "Output phyloxml file. Default: don't save.",
                    '-out-graph':'Output file to save the ITOL-compatible multi-graph values. By default, use name defined in -out, but with .csv suffix.',
                    '-out-heatmap':'Output comma separated values for upload to ITOL. Represents the presence of each taxon across datasets',
                    '-collapse-at-rank':"Desired bottom rank. e.g. genus, species. Default: Don't collapse at all.",
                    '-in':"SSUMMO results files (the ones ending in .pkl)",
#                    '--upload' : 'Upload the tree to ITOL and retrieve a pdf version. The appropriate parameters must be set in CONFIG.py',
#                    '--download' : 'Download tree(s) in format(s) specified by -out-formats',
                    '-unknowns' : 'Can either `merge` siblings into single clade, or `delete` unknowns. Default: neither.',
                    '-out-formats' : 'Image format(s) of the tree you want from ITOL. [pdf]',
                  }
        self.useage = "Useage:-\npython comparative_results.py [options] results1.pkl results2.pkl [results3.pkl] [...]"
        self.singleargs = ['-out','-out-graph','-out-heatmap','-collapse-at-rank','--download','--upload','-unknowns']
        self.multiargs  = [ '-in' , '-out-formats' ]
        self.regargs    = [ re.compile(r'^-group(\d+)') ]
        self.regopts    = {}    # if we want to group files.
        self.switches = { '--upload' : '[False] Upload files to the IToL server.\nMake sure you have a user account there and have enabled batch access (login and go to their Help page)',
                          '--download':'[False] Download files from the IToL server in requested -out-formats.\nCurrently needs to be used with --upload, i.e. does not remember uploaded tree URLs.',
                        }
        self.example = '/path/to/comparative_results.py --download --upload -in ssummo_output.pkl -collapse-at-rank genus'
        self.post_checks.append( self.local_checks )
        if args != None:
            self.parseArgs( args )
            #self.LocalParseArgs( args )
    def __getitem__(self,key):
        return self.options[key]
    def __setitem__(self,key,value):
        self.options.update( { key : value } )
    def LocalParseArgs(self,args):
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
                            prevargDash = True
                            matched = True
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
                        self.regopts.update( { command : [ arg ] } )
                else:
                    sys.stderr.write( 'Unrecognised command: {0}\n'.format( command ) )
            else:
                if '-in' in self.multiargs:
                    self.options['-in'].append( arg )
                else:
                    self.options.update( { '-in' : arg } )
        self.check_groups()
        return self.options

    def local_checks( self ):
        if self.options['-out'] == None:
            self.options['-out'] = self.get_file_name()
        elif not self.options['-out'].endswith('xml'):
            self.options['-out'] = self.options['-out'].rsplit('.',1)[0] + '.xml'
        if os.path.exists( self.options['-out'] ):
            self.options['-out'] = self.get_file_name(tried=self.options['-out'])
        if self.options['-out-heatmap'] is None and self.options['-out'] is None:
            raise ArgumentError
        elif self.options['-out-heatmap'] is None:
            out_name = self.options['-out']
            prefix = out_name[:out_name.rfind('.')]
            self.options['-out-heatmap'] = prefix + '_heatmap.csv'

    def Localcheck_groups( self ):
        reg_files = self.regopts.values() # list of lists
        n_reg_files = sum( [ len(val) for val in reg_files ] )
        if len( self.options['-in'] ) < n_reg_files:
            if len( self.options['-in'] ) > 0:
                sys.stderr.write( 'Number of group files defined differs from the number of input files.\n')
                sys.stderr.write( 'Taking files defined in groups as -in files.\n' )
                self.options['-in'] = []
            for reg_file in reg_files:
                if reg_file not in self.options:
                    self.options['-in'].append( reg_file )
                else:
                    sys.stderr.write( '{0} defined in at least once already'.format(reg_file) )
        else:
            return

    def get_file_name(self,tried=None ):
        if tried is None:
            file_name = raw_input( 'Please give a file name to save the combined results phyloxml file:-\n' )
        else:
            file_name = raw_input( '{0} exists. Try again:-'.format( tried) )
        if os.path.exists( file_name ):
            file_name = self.get_file_name( tried=file_name)
        elif file_name.strip() == "":
            sys.stderr.write( 'Need to give an option for `-out`\n' )
            exit()
        return file_name


def load_dicts( file_names ):
    print 'loading {0} pickled files'.format( len( file_names ) )
    results_dicts = []
    for f_name in file_names:
        if not f_name.endswith('.pkl'):
            new_name = f_name[:f_name.rfind('.')] + '.pkl'
            if not os.path.exists( new_name ):
                raise IOError( "{0} not a .pkl file, and {1} doesn't exist.".format( f_name, new_name ) )
            f_name = new_name
        with file( f_name,'rb') as inFile:
            results_dicts.append( pickle.load( inFile ) )
            sys.stdout.write(' .')
    return results_dicts

class ArgumentError( BaseException ):
    def __str__(self):
        return "At least '-out' needs to be defined to generate graphs!"

class GraphWriter:
    def __init__( self, results , options ,methods='default' ):
        self.initial_results = results
        self.options = options
        self.methods = { 'pre' : [ ],
                         'iter': [ ],
                         'in'  : [ ],
                         'post': [ ],
                       }
        self.spectrogram = [ colour for colour in colours.generate_HEX_colours( len( options['-in'] ) ) ]
        #Generate Heatmap colours
        if len(options.regopts) > 0:
            self.heat_colours = [colours.HSL_to_HEX(HSL) for HSL in colours.make_HSL_heatmap( len(self.options['-in']), [len(res) for res in self.options.regopts.values()] )]
        else:
            self.heat_colours = [colours.HSL_to_HEX(HSL) for HSL in colours.make_HSL_heatmap(len(self.options['-in']))]
        self.flat_heat = [colours.HSL_to_HEX(HSL) for HSL in colours.make_HSL_heatmap(len(self.options['-in']))]
        #If the results are grouped, then we will use the heatmap generator for the graphs too, otherwise normal spectrogram.
        if len( self.options.regopts ) > 0:
            self.graph_colours = self.heat_colours
        else:
            self.graph_colours = self.spectrogram
        self.uncertains = re.compile( r'(uncultured)|(unknown)|(incertae)',re.I)
        self.spaceSub = re.compile( r'\s+' )
        self.taxDict = load_index()
        if methods == 'default':
            self.default()
        self.in_file_names = [ opt.rsplit(os.path.sep,1)[-1] for opt in self.options['-in'] ]
        self.found = set()
    
    def add_method( self , method, fn, *args, **kwargs ):
        """When comparing results, which is a recursive process, there
        are a number of places with which to attach methods. `method`
        indicates where in the process to attach the function `fn`.
        Allowed `method`:-
            'pre'  - Methods called before we start recursing the tree. By default,
                    this initialises output files and combines thre results dictionaries.
            'iter' - A generator function for iterating through results dictionaries.
                     Each iter method needs it's own consumer method too.
                     The generator will thus yield an item that is passed to the given 
                     method.
                     This must be defined with the extra kwarg:-
                        'meth'
            'in'   - The default 'meth' is itereator. This calls every method referenced
                    by 'in', in the order specified by self.methods.in
            'post' - Closing methods.

        fn should be a reference to a function.

        *args and **kwargs are dependent on the fn given.
        """
        self.methods[method].append( { 'fn'    : fn,
                                       'args'  : args,
                                       'kwargs': kwargs, } )
        if method == 'iter':
            self.methods[method][-1].update( { 'meth' : kwargs['meth'] } )
    
    def init_heatmap( self, *args, **kwargs ):
        self.heatmap_out = file( self.options['-out-heatmap'] ,'w' )
        try:
            self.heatmap_out.write( 'LABELS,' + ','.join( [ group[0].split('.',1)[0] for group in self.options.regopts.itervalues() ] ) +' \n')
        except TypeError:
            print self.options.regopts.items()[0]
            raise
    def init_colorstrip( self, *args, **kwargs ):
        self.options['-out-colorstrip'] = self.options['-out'].rsplit( '.' )[0] + '_strip.csv'
        self.colorstrip = file( self.options['-out-colorstrip'] ,'w' )

    def init_graph( self, *args, **kwargs ):
        ### For abundance graphs.
        if self.options['-out-graph'] == None and self.options['-out'] == None:
            raise ArgumentError
        elif self.options['-out-graph'] == None:
            out_name = options['-out']
            prefix = out_name[:out_name.rfind('.')]
            options['-out-graph'] = prefix + '.csv'
        self.graph_out = file( options['-out-graph'] , 'w' )
        self.graph_out.write( 'LABELS,' + ','.join([dataset_name.rsplit('.',1)[0].split( os.path.sep)[-1] for dataset_name in self.options['-in']] ) +' \n' )
        self.graph_out.write( 'COLORS,' + ','.join( self.graph_colours ) +'\n' )

    def init_colours( self , *args , **kwargs ):
        colour_file_name = self.options['-out'][:self.options['-out'].rfind('.')]+'_ITOL_colours.txt'
        self.colour_file = file( colour_file_name ,'w')
        self.colours , self.colour_indexes = make_colours( self.combined_dict , self.taxDict )

    def init_xml( self, *args, **kwargs ):
        if self.options['-out'] is None:
            raise ArgumentError( "Need to define options['-out']" )
        self.tree_out = file( self.options['-out'] ,'w' )
        self.tree_out.write('<phyloxml>\n')
        self.tree_out.write('<phylogeny rooted="false">\n')#<clade branch_length="1.0"><name>root</name>\n')

    def close_files( self ):
        with file( self.options['-out'].rsplit('.',1)[0] + '.pkl' ,'wb' ) as outfile:
            pickle.dump(self.combined_dict, outfile , -1 )
        if not self.graph_out.closed:
            self.graph_out.write( '\n' )
            self.graph_out.close()
        if not self.colorstrip.closed:
            self.colorstrip.write( '\n' )
            self.colorstrip.close()
        if not self.heatmap_out.closed:
            self.heatmap_out.write( '\n' )
            self.heatmap_out.close()
        if not self.colour_file.closed:
            self.colour_file.close()

    def _merge( self , path , results_node ):
        combined_accs = [ [] for i in xrange( len(self.options['-in'] ) ) ]
        uncertain = False
        for node_name in sorted( results_node.keys() ):
            if self.uncertains.search( node_name ):
                self.count += 1
                uncertain = True
                combined_accs = get_combined_accessions( results_node.pop( node_name ) , accessions=combined_accs ) 
        if uncertain:
            try:
                parent, taxon = path.rsplit( os.path.sep,2 )[-2:]
            except ValueError:
                combined_name = 'unknown {0}'.format( path.strip( os.path.sep ) )
            else:
                combined_name = 'unknown {0}'.format( parent )
            results_node.update( { combined_name : {'accessions' : combined_accs } } )
        return results_node

    def _del( self , path , results_node ):
        new_results = {}
        #combined_accs = [ [] for i in xrange( len(self.options['-in'] ) ) ]
        for node_name in sorted( results_node.keys() ):
            if self.uncertains.search( node_name ):
                self.count += 1
                results_node.pop( node_name )
        #        combined_accs = get_combined_accessions( results_node.pop( node_name ) , accessions=combined_accs ) 
            else:
                new_results.update( { node_name : results_node.pop( node_name )} )
        results_node.update( new_results )
        return new_results

    def unknowns( self ):
        self.count = 0
        if self.options['-unknowns'] == 'merge':
            fn = self._merge
        elif self.options['-unknowns'].startswith('d'):
            fn = self._del
        else:
            sys.stderr.write( 'Not doing anything with unknowns. Command argument was: {0}'.format( self.options['-unknowns'] ) )
            return
        new_tree = {}
        for full_path,results_node in dict_walk( '' , self.combined_dict , topdown=False, random=False ):
            if full_path == '':
                continue
            # Call either _merge or _del.
            node = fn( full_path, results_node )
            #sub_accs = get_combined_accessions( node , accessions = blank_accs[:] ) 
            blank_accs = [ [] for i in xrange( len(self.options['-in'] ) ) ]
            n_accs = sum( [len(a) for a in get_combined_accessions( node, accessions=blank_accs )] ) 
            # Traverse new tree & update with results node, only if there are accessions to speak of.
            if n_accs > 0:
                new_node = new_tree
                for path in full_path.split( os.path.sep ):
                    if path not in new_node:
                        new_node.update( { path : {} } )
                    new_node = new_node[path]
                new_node.update( node )
            else:
                self.count += 1
                print 'deleting node {0}'.format( full_path )
        del( self.combined_dict )
        self.combined_dict = new_tree
        action = 'merged' if fn == self._merge else 'deleted'
        print '{0} {1} unknowns'.format( action, self.count )

    def default( self ):
        self.add_method( 'pre' , self.init_heatmap      )
        self.add_method( 'pre' , self.init_graph        )
        self.add_method( 'pre' , self.init_colorstrip   )
        self.add_method( 'pre' , self.combine_dicts     )
        self.add_method( 'pre' , self.init_xml          )
        self.add_method( 'pre' , self.init_colours      )
        if self.options['-unknowns'] is not None:
            self.add_method( 'pre' , self.unknowns )
        self.add_method( 'iter', self.generator         ,meth=self.itereater )
        self.add_method( 'in'  , self._write_graph      ) 
        self.add_method( 'in'  , self.write_colorstrip  ) 
        self.add_method( 'in'  , self.write_heatmap     )
        self.add_method( 'in'  , self.write_xml         )
        self.add_method( 'in'  , self.colour_node       )
        self.add_method( 'post', self.close_xml         )
        self.add_method( 'post', self.close_files       )

    def combine_dicts( self ):
        self.combined_dict = combine_dicts( self.initial_results )
        if self.options['-collapse-at-rank'] is not False:
            self.combined_dict = collapse_at_rank( self.combined_dict, self.options, TaxDB(), self.taxDict, combined=True)

    def run( self ):
        for meth in self.methods['pre']:
            meth['fn']( *meth['args'] , **meth['kwargs'] )
        try:
            for meth in self.methods['iter']:
                for generated_item in meth['fn']():
                    meth['meth']( generated_item )
        except (KeyboardInterrupt, Exception ):
            raise

        for method in self.methods['post']:
            method['fn']( *method['args'] , **method['kwargs'] )

    def colour_node( self ,unique_name , node ):
        colour_node( self.tax_path , self.colour_indexes , self.colour_file , self.colours )

    def generator( self ):
        self.totals = [ float(len(accs)) for accs in get_combined_accessions( self.combined_dict, [ [] for i in xrange( len(self.options['-in'] ) ) ] ) ]
        self.prev_depth = 0
        for tax_path , node in dict_walk( '', self.combined_dict,random=False ):
            tax_nodes = tax_path.rstrip(os.path.sep).split( os.path.sep )
            self.diff_from_original = len( tax_nodes )
            unique_name = self.unique_taxon( tax_nodes )
            self.tax_path = tax_nodes
            self.tax_path[-1] = unique_name
            yield ( unique_name , node )
            self.prev_depth = self.diff_from_original

    def itereater( self , taxpath_node ):
        unique_name , node = taxpath_node
        for method in self.methods['in']:
            method['fn']( unique_name, node )

    def unique_taxon( self , tax_nodes ):
        if self.uncertains.search( tax_nodes[-1] ) and not self.uncertains.search( tax_nodes[-2] ):
            last_node = re.compile( r'|'.join( tax_nodes[-1].split(' ') ) )
            if not last_node.search( tax_nodes[-2] ):
                end_node = '_'.join( tax_nodes[-1:-3:-1] )
            else:
                end_node = tax_nodes[-1]
        elif tax_nodes[-1].strip() == '':
            self.found.add( "root" )
            return "root"
        else:
            end_node = tax_nodes[-1]
        n = 1   ## Make each node name unique
        end_node = self.spaceSub.sub( '_' , end_node )
        while end_node in self.found:
            end_node = end_node.rstrip( '_{0}'.format(n) )
            n += 1
            end_node = '{0}_{1}'.format(end_node,n)
        self.found.add( end_node )
        return end_node

    def write_xml( self, unique_name , node ):
        diff = self.diff_from_original - self.prev_depth
        distance = 0.5 / self.diff_from_original
        nodes = node.keys()
        if diff == 1: ## 1 is the highest it should ever be...
            self.tree_out.write(('\t' * self.diff_from_original ) + '<clade branch_length="%.2f">' % (distance) )
            if len(nodes) == 0 or nodes == ['accessions']:
                self.tree_out.write('<name>{0}</name></clade>\n'.format(unique_name))
                ### Colour Node.
            else:
                self.tree_out.write('<name>{0}</name>'.format(unique_name))
                self.tree_out.write('\n')
                pass
        elif diff == 0:  ## Traversing empty folders in one directory
            self.tree_out.write(str('\t' * self.diff_from_original) + '<clade branch_length="%.2f">' % (distance) )
            if len(nodes) == 0 or nodes == ['accessions']:
                self.tree_out.write('<name>{0}</name></clade>\n'.format(unique_name))
            else:
                self.tree_out.write('<name>{0}</name>'.format(unique_name ))
                self.tree_out.write('\n')
                pass
        elif diff < 0:
            for i in xrange(self.prev_depth, self.diff_from_original, -1):
                self.tree_out.write('\t' * ( i - 1))
                if i == self.prev_depth:
                    self.tree_out.write('</clade>\n')
                elif i == self.diff_from_original:  ## was elif
                    self.tree_out.write('</clade>\n')
                else:
                    self.tree_out.write('</clade>\n' )#+ ('\t' * i) + '</ul>\n')
            self.tree_out.write(str('\t' * self.diff_from_original) + str('<clade branch_length="%.2f">' % (distance) ) )
            if len(nodes) == 0 or nodes == ['accessions']:
                self.tree_out.write('<name>{0}</name></clade>\n'.format(unique_name) )
            else:
                self.tree_out.write('<name>{0}</name>'.format(unique_name))
                self.tree_out.write('\n')
        else:
                print "Jumped more than one (%s) directories forward.. no no no..." % str(diff)

    def close_xml( self ,*args,**kwargs):
        for i in xrange(self.prev_depth, 0, -1): 
            self.tree_out.write( '{0}</clade>\n'.format('\t' * (i-1)) )
        self.tree_out.write('</phylogeny>\n')
        self.tree_out.write('</phyloxml>\n')
        self.tree_out.close()

    def _write_graph( self , unique_name , node ):
        if 'accessions' in node:
            combined_accessions = node['accessions']
            self.graph_out.write( unique_name )
            output = ''
            self.nfound = 0
            for i, accessions in enumerate( combined_accessions ):
                N = len(accessions)
                if N == 0:
                    output += ',0'
                else:
                    self.nfound += 1
                    output += ',{0}'.format( 100 * N / self.totals[i] )
            self.graph_out.write( output + ' \n' )

    def write_colorstrip( self , unique_name , node):
        #ubiquity
        if 'accessions' in node and len( node ) == 1:
            try:
                self.colorstrip.write( '{0},{1} \n'.format( unique_name , self.flat_heat[self.nfound-1] ) )
            except IndexError:
                print self.nfound
                raise

    def write_heatmap( self, unique_name , node ):
        # Group ubiquity
        if 'accessions' in node and len( node ) == 1:
            self.heatmap_out.write( unique_name )
            for group in self.options.regopts.itervalues():
                #group = self.options.regopts[group_ID]
                n_found = 0
                N = len( group )
                for index, file_name in enumerate( group ):
                    acc_index = self.in_file_names.index( file_name.rsplit( os.path.sep , 1)[-1] )  # Just get the filename, no path.
                    if len(node['accessions'][acc_index]) > 0:
                        n_found += 1
                self.heatmap_out.write( ',{0}'.format( 100. * (float(n_found) / N) ) )
            self.heatmap_out.write( ' \n' )


    ### UNUSED METHODS  ###
    def uniqueify( self ):
        new_dict = {}
        for tax_path, node in dict_walk( '', self.combined_dict, random=False ):
            tax_nodes = tax_path.split( os.path.sep )
            new_node = new_dict
            unique_name = self.spaceSub.sub( '_' , self.unique_taxon( tax_nodes ) )
            for tax_node in tax_nodes[:-1]:
                if tax_node == "":
                    continue
                if tax_node not in new_node:
                    new_node.update( { tax_node : {} } )
                new_node = new_node[tax_node]
            if tax_nodes != [""]:
                new_node.update( { unique_name : {} } )
                new_node = new_node[unique_name]
                if 'accessions' in node:
                   new_node.update( { 'accessions' : node['accessions'] } )

    def iter_groups( self , *args, **kwargs ):
        if len( self.options.regopts ) > 0:
            self.init_colorstrip()
            self.add_method( 'post' , self.close_colorstrip() ,[] , {} )
            combined_results = []
            for group_files in self.options.regopts.itervalues():
                single_dicts = []
                for _file in group_files:
                    with file( _file ,'rb') as results_file:
                        single_dicts.append( pickle.load( results_file ) )
                combined_results.append( self.combine_dicts( single_dicts ) )
                yield combined_results

def ITOLupload( graph_name, heatmap_name, ITOLOptionDict):
    itol_uploader = Itol.Itol()
    XMLname = ITOLOptionDict.pop('treeFile')
    itol_uploader.set_tree_location( XMLname )
    itol_uploader.add_upload_param_dict( ITOLOptionDict )
    abundance_dataset = Dataset.Dataset()
    abundance_dataset.set_dataset_location( graph_name )
    abundance_dataset.add_param_dict( { 'Label' : '%seqs per OTU', 'Type':'multibar','Separator':'comma','MultiBarAlign':'1' } )
    itol_uploader.add_dataset( abundance_dataset )
    heatmap_dataset = Dataset.Dataset()
    heatmap_dataset.set_dataset_location( heatmap_name )
    heatmap_dataset.add_param_dict( { 'Label' : 'Presence over datasets.' , 'Type':'colourstrip','Separator':'comma' } )
    good_upload = itol_uploader.upload_tree()
    if not good_upload:
        print 'Error!\n',itol_uploader.upload_output()
    webpage = itol_uploader.get_webpage()
    print 'Tree Web Page URL:    {0}'.format(webpage)
    return itol_uploader

def ITOLdownload( graph_name, itol_uploader,ITOLDownloadOptions={},formats=['pdf'] ):
    itol_exporter = itol_uploader.get_itol_export()
    prefix = graph_name[:graph_name.rfind('.')]
    for suffix in formats:
        exportLocation = '{0}.{1}'.format(prefix,suffix)
        itol_exporter.add_export_param_dict( ITOLDownloadOptions )
        itol_exporter.set_export_param_value('format',suffix)
        itol_exporter.set_export_param_value('datasetList','dataset1')
        itol_exporter.export(exportLocation)
        print 'exported {0} formatted tree to {1}.'.format(suffix, exportLocation )


def main(options):
    results_dicts = load_dicts( options['-in'])
    grapher = GraphWriter( results_dicts , options )
    grapher.run( )
    options = grapher.options
    sys.stdout.write( '\n######  OUTPUT FILES ######\n')
    sys.stdout.write( '\n{0}{1}\n'.format( 'phyloxml tree saved at:'.ljust(40), options['-out'] ))
    sys.stdout.write( '{0}{1}\n'.format( 'ITOL multi-value bar chart saved at:'.ljust(40), options['-out-graph'] ))
    colour_file_name = grapher.colour_file.name
    sys.stdout.write( '{0}{1}\n'.format( 'ITOL colour file saved at:'.ljust(40), colour_file_name ))

    ### IToL UPLOAD & Download ##
    heat_gen = lambda x: [colours.HSL_to_HEX(HSL) for HSL in colours.make_HSL_heatmap(x)]

    if len( options['-in'] ) % 2 != 0:
        heat_colours = heat_gen( len( options['-in'] )+1 )
    elif len( options['-in'] ) == 2:
        heat_colours = heat_gen( 4 )
    else:
        heat_colours = grapher.heat_colours
    mid_heat_colour = heat_colours[ len( heat_colours ) / 2 ]
    if options['--upload']:
        with file( options['-out'] ,'r' ) as outFile:
            with file( colour_file_name ,'r' ) as colourFile:
                with file( options['-out-graph'] , 'r' ) as graphFile:
                    with file( options['-out-colorstrip'],'r' ) as stripFile:
                        with file( options['-out-heatmap'],'r' ) as heatFile:
                            ITOL = ITOLCGI( out_file = outFile, colour_file = colourFile )
                            ITOL.add_dataset( graphFile )
                            ITOL.add_dataset( stripFile,
                                                options= {'Label' :'Ubiquity',
                                                  'Type'      :   'colorstrip',
                                                  'Separator' :   'comma'
                                                         }
                                            )
                            ITOL.add_dataset( heatFile,
                                                options = {'Label'     : 'Group_ubiquity',
                                                           'Type'      : 'heatmap',
                                                           'Separator' : 'comma',
                                                           'HeatmapBoxWidth': '10',
                                                           'MinPointValue' : "-100",
                                                           'MidPointValue' : "0",
                                                           'MaxPointValue' : "100",
                                                           'MinPointColor' : heat_colours[0],
                                                           'MidPointColor' : mid_heat_colour,
                                                           'MaxPointColor' : heat_colours[-1],
                                                           }
                                            )
                            print heat_colours[0], mid_heat_colour , heat_colours[-1]                                                        
                            uploader = ITOL.ITOLupload( )
        if options['--download']:
            if len(options['-out-formats']) == 0:
                options['-out-formats'].append('pdf')
            ITOL.ITOLdownload(formats=options['-out-formats'])

if __name__ == '__main__':
    args = sys.argv[1:]
    options = LocalOptions(args)
    main(options)
