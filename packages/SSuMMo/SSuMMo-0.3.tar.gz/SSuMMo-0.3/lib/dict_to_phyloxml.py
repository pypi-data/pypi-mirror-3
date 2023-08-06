#!/usr/bin/env python
"""
This script creates a phyloxml formatted tree from a ssummo results file.
It's most useful because it contains the functions in order to make that
phyloxml, so is called by comparative_results.py and SSUMMO.py.

Useage:-
python dict_to_phyloxml.py /path/to/SSuMMoresults.pkl

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
# Creates phyloxml formatted tree from a SSuMMo results dictionary.
# Simple as that.
#
# Useage:-
# python dict_to_phyloxml.py /path/to/results.pkl
import sys
import os
import re
from ssummolib import my_walk,TaxDB,fetchRank, find_start_node, dict_walk, Options
import cPickle as pickle
import CONFIG
from colours import generate_HEX_colours

def colour_node(path_list, colour_indexes, out_handle,colours):
    """Colours each node by the 2nd level from root, by creating an ITOL-compatible
    colour index file for uploading to colour the leaves.
    """
    ### Colour Node.
    try:
        x = colour_node.cache
        del(x)
    except AttributeError:
        colour_node.cache = set()
    for OTU in path_list:
        if OTU in colour_indexes:
            out_handle.write('{0}\trange\t{1}\t{2}\n'.format( path_list[-1], colours[colour_indexes[OTU ] ], OTU ))
            if OTU not in colour_node.cache:
                colour_node.cache.add(OTU)
                print "{0} being assigned colour {1}".format(OTU, colours[colour_indexes[OTU]])
            return

def number_of_leaves( node ):
    n = 0
    for path, node in dict_walk( '', node ):
        branches = node.keys()
        n_branches = len( branches )
        if (n_branches == 1 and 'accessions' in branches) or n_branches == 0:
            n += 1
        else:
            continue
    return n

def make_colours(results_dict, taxDict, colour_rank = 'phylum'):
    """Results_dict is the results we're gonna be turning into phyloxml.
    taxDict is the complete ARB taxonomy dictionary.
    colour_rank is the rank at which you want to colour.
    """
    rank_reg = re.compile( colour_rank, re.I )
    colour_indexes = {}
    phyla = []
    taxDBObj = TaxDB()
    taxDict, fullPath = find_start_node( results_dict, taxDict )
    startPathPosition = len(CONFIG.arbDBdir) + 1
    if ('Eukaryota' and ('Archaea' or 'Bacteria')) in results_dict.keys():
        table = 'Prokaryotes'
    elif 'Eukaryota' in fullPath or 'Eukaryota' in results_dict.keys():
        table = 'Eukaryotes'
    else:
        table = 'Prokaryotes'
    ### Find the OTU names at rank of interest.
    for path,node in dict_walk( fullPath, results_dict ):
        path_list = path.split( os.path.sep )
        found = False
        for phylum in phyla:  # This little loop to reduce MySQL queries (in fetchRank).
            if phylum in path_list:
                found = True
                break
        if found:
            continue
        for i in xrange(1,len(path_list)):
            rank,name = fetchRank( taxDBObj , table, path_list[i],parent_name=path_list[i-1] )
            if rank != False:
                if rank_reg.search( rank ):
                    phyla.append( path_list[i] )
                    break # to next (path,node) from dict_walk.
        if not found:
            table = set((table,)).symmetric_difference( set( ('Prokaryotes','Eukaryotes',)) ).pop()
    if len(phyla) == 0:
        print "No {0} found!!".format( colour_rank )
        return 0,[]
    colours = [ colour for colour in generate_HEX_colours( len(phyla) ) ]
    ## Sort in order of number of leaves from that node.
    phylaReg = re.compile( '|'.join( phyla ) )
    count = 0
    counts = {}  ## First, count the number of nodes.
    for path, node in dict_walk( '', results_dict ):
        path_list = path.split( os.path.sep )
        phylaFind = phylaReg.search( path_list[-1] )
        if phylaFind:
            phylaFound = phylaFind.group()
            if phylaFound not in counts:
                count = number_of_leaves( node )
                counts.update( { phylaFound : count } )
        else:
            continue
            #count += 1
    ## Second, sort by number of nodes, then alphabetical.
    number_nodes = sorted(counts.values())
    for i in xrange(len(number_nodes)):
        count = number_nodes[i]
        if number_nodes.count( count ) > 1:
            thisMany = []
            for phylum in counts:
                if counts[phylum] == count:
                    thisMany.append( phylum )
            thisMany = sorted( thisMany )
            for thisone in thisMany:
                if thisone not in colour_indexes:
                    colour_indexes.update( {thisone : i })
                    break
        else:
            for phylum in counts:
                if counts[phylum] == count:
                    colour_indexes.update( { phylum: i } )
    return colours, colour_indexes 

def write_xml(top, tree_out, results_dict, tax_dict, colour_rank = 'phylum' ):
    spaceSub = re.compile( r'\s+' )
    dir_count = 0
    tree_out.write('<phyloxml>\n')
    tree_out.write('<phylogeny rooted="false">\n<clade branch_length="1.0"><name>root</name>\n')
    ## Prep the Colour File ##
    colour_file_name = tree_out.name[:tree_out.name.rfind('.')]+'_ITOL_colours.txt'
    colours_out = file( colour_file_name ,'w')
    colours,colour_indexes = make_colours(results_dict, tax_dict, colour_rank = colour_rank)
    ###########################
    if type(results_dict) != dict or len(results_dict.keys()) == 0:
            print 'results_dict either empty, or not a dictionary!!\nExiting...'
            exit()
    found = set()
    uncertains = re.compile( r'(uncultured)|(unknown)|(incertae)',re.I )
    for domain in sorted(results_dict.keys()):
        if domain == 'accessions':
            continue
        top_path = os.path.join(top ,domain )
        prev_depth = top_path.count( os.path.sep ) ## This changes each iteration of the loop
        original_depth = prev_depth                ## This will remain unchanged throughout.
        node = results_dict[domain]
        for path, folders in my_walk( top_path , node,random=False):
            path = path.rstrip( os.path.sep )
            path_list = path.split( os.path.sep )
            if path_list[-1] == 'accessions':
                #### Can do loads of colour stuff here!! ####
                pass
            dir_count += 1
            depth = path.count( os.path.sep )
            diff = depth - prev_depth
            diff_from_original = depth - original_depth
            if diff_from_original == 0:  ## Figure out pretty, proportional branch lengths.
                distance = 0.5
            else:
                distance = float(0.5)/float(diff_from_original)
            end_node = path_list[-1]  ## Figure out if information is useless (incertae / unknown / uncultured )
            ## Figure out if information is useless (incertae / unknown / uncultured )
            if uncertains.search( end_node) and not uncertains.search(path_list[-2]):
                last_node = re.compile( r'|'.join( end_node.split(' ') ) )
                if not last_node.search( path_list[-2] ) :
                    end_node = '_'.join(path_list[-1:-3:-1])
                else:
                    end_node = path_list[-1]
            elif path_list[-1].strip() == "":
                end_node = "root"
            n = 0
            end_node = spaceSub.sub( '_' , end_node )   ## Figure out if information is useless (incertae / unknown / uncultured )
            while end_node in found:  ## Make node names unique
                end_node = end_node.rstrip( '_{0}'.format(n) )
                n += 1
                end_node = '{0}_{1}'.format(end_node,n)
            found.add( end_node )
            path_list[-1] = end_node
            if diff == 1: ## 1 is the highest it should ever be...
                tree_out.write(('\t' * diff_from_original ) + '<clade branch_length="%.2f">' % (distance) )
                if len(folders) == 0 or folders == ['accessions']:
                    tree_out.write('<name>{0}</name></clade>\n'.format(end_node))
                    ### Colour Node.
                else:
                    tree_out.write('<name>{0}</name>'.format(end_node))
                    tree_out.write('\n')
                    pass
            elif diff == 0:  ## Traversing empty folders in one directory
                tree_out.write(str('\t' * diff_from_original) + '<clade branch_length="%.2f">' % (distance) )
                if len(folders) == 0 or (folders == ['accessions'] and path != top_path):
                    tree_out.write('<name>{0}</name></clade>\n'.format(end_node))
                else:
                    tree_out.write('<name>{0}</name>'.format(end_node ))
                    tree_out.write('\n')
                    pass
            elif diff < 0:
                for i in range(prev_diff_from_original, diff_from_original , -1):
                    tree_out.write('\t' * ( i - 1))
                    if i == prev_diff_from_original:
                        tree_out.write('</clade>\n')
                    elif i == diff_from_original:  ## was elif
                        tree_out.write('</clade>\n')
                    else:
                        tree_out.write('</clade>\n' )#+ ('\t' * i) + '</ul>\n')
                tree_out.write(str('\t' * diff_from_original) + str('<clade branch_length="%.2f">' % (distance) ) )
                if len(folders) == 0 or folders == ['accessions']:
                    tree_out.write('<name>{0}</name></clade>\n'.format(end_node) )
                else:
                    tree_out.write('<name>{0}</name>'.format(end_node))
                    tree_out.write('\n')
                    pass
            else:
                    print "Jumped more than one (%s) directories forward.. no no no..." % str(diff)
                    print path
            colour_node(path_list, colour_indexes, colours_out,colours)
            prev_depth = depth
            prev_path = path
            prev_diff_from_original = diff_from_original
        ## Need to close off the appropriate number of '</ul>'s and </li>'s
        for i in range(prev_diff_from_original, 0, -1): 
                tree_out.write( '{0}</clade>\n'.format('\t' * (i-1)) )
    colours_out.write('\n')
    colours_out.close()
    tree_out.write('</clade>\n')
    tree_out.write('</phylogeny>\n')
    tree_out.write('</phyloxml>\n')

if __name__ == '__main__':
    args = sys.argv[1:]
    options = Options( args )
    with file(CONFIG.taxIndex,'rb') as index_file:
        tax_dict = pickle.load(index_file)
    for in_file in options['-in']:
        with file( in_file,'rb') as result_file:
            result_dict = pickle.load( result_file )
        #if '.' in options['-in'][ options['-in'].rfind( os.path.sep) :]:
        if '.' in in_file[ in_file.rfind( os.path.sep) :]:
            output_name = in_file[ : in_file.rfind('.')] + '.xml'
        else:
            output_name = in_file + '.xml'
        write_handle = file(output_name,'w')
        write_xml(CONFIG.top, write_handle, result_dict, tax_dict)
        os.chmod(output_name ,0755)


