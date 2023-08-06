#!/usr/bin/env python
"""This script creates an html file that represents the directory hierarchy
which it searches. Provide a path as first system argument, and this will
represent the subdirectory hierarchies as a dynamic web page.

Useage:-
python dict_to_html.py [SSUMMO_output].pkl

******

*** The file folder_initiate.html must be in the html directory, which
***  you should have received with all the SSuMMo scripts.

*** For the html page to work correctly, the following files need to be
*** found by the web server, as are linked to by the generated html.
***	simpletree.css
***	simpletreemenu.js

******

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
# Creates html from SSuMMo results dictionary. Requires
#    html/folder_initiate.html
# When placed in a web server directory, need to ensure that the 
# following files are linked to properly:-
#    html/simpletree.css
#    html/simpletreemenu.js
# By default, the generated html assumes that they will be found in
# the following web directories (relative to site root):-
#    /styles/simpletree.css
#    /js/simpletreemenu.js
# If you want or need to change the location of these files, then you'll
# need to change those links in html/folder_initiate.html (lines 2 & 12)
# 
import sys
import os
import cPickle as pickle
import re
from colours import generate_HEX_colours
from ssummolib import dict_walk, get_accessions
import CONFIG
try:
	import MySQLdb
	CONFIG.mySQLcur = MySQLdb.connect(user=CONFIG.user,host=CONFIG.host,passwd=CONFIG.passwd,db=CONFIG.db).cursor()
except ImportError:
	print "Missing dependency - python MySQLdb"

def write_html(startDir, html_out, taxDict):
	domMatch = re.compile( r'(Bacteria)|(Archaea)|(Eukaryota)' )
	dir_count = 0
	tableMatch = domMatch.search( startDir )
	if startDir == CONFIG.arbDBdir:
		node_keys = taxDict.keys()
	elif tableMatch:
		parent = startDir.rstrip(os.path.sep).split( os.path.sep )[-1]
		node_keys = [parent]
		top_path = startDir
	else:
		print "Won't be able to assign rank information as can't find the domain!!"
	for key in node_keys:
		if startDir == CONFIG.arbDBdir:
			top_path = os.path.join( startDir,key )
			tableMatch = domMatch.search( top_path )
			parent = 'root'
			if tableMatch:
				if tableMatch.groups()[2]:
					table = 'Eukaryotes'
				else:
					table = 'Prokaryotes'
			else:
				table = None
			node = taxDict[key]
		elif tableMatch:
			if tableMatch.groups()[2]:
				table = 'Eukaryotes'
			else:
				table = 'Prokaryotes'
			node = taxDict
		else:
			print "Won't be able to assign rank information as can't find the domain!!"
		prev_depth = top_path.count( os.path.sep ) ## This changes each iteration of the loop
		original_depth = prev_depth		   ## This will remain unchanged throughout.
		for path, taxNode in dict_walk( os.path.realpath(top_path) , node):
			if path == 'accessions':
				continue
			subNodes = sorted(taxNode.keys())
			path_list = path.split( os.path.sep )
			dir_count += 1
			depth = path.count( os.path.sep )
			## prev_depth exists from previous iteration.
			diff = depth - prev_depth
			diff_from_original = depth - original_depth
			end_node = path_list[-1]
			nAssigned = len( get_accessions(taxNode,accessions=[]) )
			if 'accessions' in taxNode.keys() and len(subNodes) > 1:
				nAssigned = str(nAssigned) + '(' + str(len(taxNode['accessions'])) +')'
			if not domMatch.search( end_node ):
				parent = path_list[-2]
			rank = getRank( CONFIG.mySQLcur , end_node, parent,table )
			if rank == None or rank == 'None':
				rank = 'norank'
			if 'uncultured' in end_node:
				end_node = ' '.join(path_list[-2:])
			if diff == 1: ## 1 is the highest it should ever be...
				html_out.write( '{0}<li><div id="{1}">{2}</div> <div id="N">{3}</div>'.format( '\t' * diff_from_original,rank , end_node ,nAssigned ) )
				if len(subNodes) == 0 or subNodes == ['accessions']:
					html_out.write('</li>\n')
				else:
					html_out.write('\n' + ('\t' * (diff_from_original + 1) ) + '<ul>\n')
			elif diff == 0:  ## Traversing empty folders in one directory
				html_out.write( '{0}<li><div id="{1}">{2}</div>'.format( '\t' * diff_from_original,rank , end_node ) )
				html_out.write( '<div id="N">{0}</div>'.format( nAssigned ) )
				if len(subNodes) == 0 or subNodes == ['accessions']:
					html_out.write('</li>\n' )
				else:
					html_out.write('\n' + str('\t' * (diff_from_original + 1) ) + '<ul>\n')
			elif diff < 0:
				for i in range(prev_diff_from_original, diff_from_original -1, -1):
					html_out.write('\t' * i)
					if i == diff_from_original+1 and i == prev_diff_from_original:
						html_out.write('</ul>\n')# + ('\t'* (i-1)) +'</li>\n' )
					elif i == prev_diff_from_original:
						html_out.write('</ul>\n'  )
					elif i == diff_from_original :
						html_out.write('</li>\n')
					else:
						html_out.write('</li>\n' + ('\t' * i) + '</ul>\n')
				html_out.write( '{0}<li><div id="{1}">{2}</div>'.format( '\t' * diff_from_original,rank , end_node ) )
				html_out.write( '<div id="N">{0}</div>'.format( nAssigned ) )
				if len(subNodes) == 0 or subNodes == ['accessions']:
					html_out.write('</li>\n'  )
				else:
					html_out.write('\n' + str((diff_from_original + 1) * '\t') + '<ul>\n')
			else:
				print "Jumped more than one (%s) directories forward.. no no no..." % str(diff)
				print path
			prev_depth = depth
			prev_path = path
			prev_diff_from_original = diff_from_original
		for i in range(prev_diff_from_original, 0, -1):
			html_out.write( '{0}</ul>\n'.format('\t' * (i-1)) )
		## Need to close off the appropriate number of '</ul>'s and </li>'s
	html_out.write('</ul>\n')

def write_css( handle,ranks,colours ):
	handle.write( """<style type="text/css">\n#N {
		position: absolute;
		right: 0;
		display: inline;
		text-align: right;
		width: 10em;\n}\n""")
	N = len(ranks)
	for i in xrange(len(ranks)):
		handle.write( '#{0}'.format(ranks[i]))
		handle.write( ' {\n' ) 
		handle.write( '    color: {0};\n'.format(colours[i] ) )
		handle.write( '    display: inline;\n' )
		handle.write( '}\n' )
	handle.write( '</style>' )

def getAllRanks(tdict,startDir,MySQLcur,parent='root'):
	"""Given the results dict and a MySQLdb cursor instance, returns a list
	of all unique taxonomic ranks present in the results dictionary"""
	rankSet = set()
	domMatch = re.compile( r'(Bacteria)|(Archaea)|(Eukaryota)' )
	for path, nodes in dict_walk(startDir,tdict):
		table = domMatch.search(path)
		if table:
			table = 'Eukaryotes' if table.groups()[2] else 'Prokaryotes'
		else:
			print "No domain found in",path
			continue
		taxPath = path.split( os.path.sep )
		OTU = taxPath[-1]
		if parent != 'root':
			if len( taxPath ) > 1:
				parent = taxPath[-2]
			else:
				parent = 'root'
		MySQLcur.execute('select * FROM NonUniques WHERE ParentName="{0}" AND Name="{1}";'.format(parent,OTU))
		NonUniques = MySQLcur.fetchall()
		if len(NonUniques) > 0:
			print "NonUnique entry found:",NonUniques
			continue
		MySQLcur.execute( 'SELECT Rank from {0} where ParentName="{1}" AND Name="{2}";'.format( table, parent,OTU ) )
		ranks = set( (r[0] for r in MySQLcur.fetchall()) )
		if len(ranks) == 0:
			MySQLcur.execute('SELECT Rank from {0} where Name="{1}";'.format( table, OTU ))
			ranks = set( rank[0] for rank in MySQLcur.fetchall() )
			if len(ranks) == 0:
				ranks = set(['norank'])
			print 'OTU',OTU,'\nparent:',parent,'\ntable:',table
		for rank in ranks:
			rankSet.add(rank.replace(' ',''))
		parent = OTU
	return sorted(list(rankSet))

def getRank( MySQLcur,OTU,parent,table ):
	MySQLcur.execute( 'SELECT Rank FROM {0} WHERE Name="{1}" AND ParentName="{2}";'.format( table,OTU,parent ) )
	rankSet = set( rank[0] for rank in MySQLcur.fetchall() )
	if len(rankSet) == 1:
		return rankSet.pop().replace(' ','')
	elif len(rankSet) == 0:
		MySQLcur.execute( 'SELECT Rank FROM {0} WHERE Name="{1}";'.format( table, OTU ) )
		rankSet = set( rank[0] for rank in MySQLcur.fetchall() )
		if len(rankSet) == 1:
			return rankSet.pop().replace(' ','')
	else:
		return '0'

def initiate_html(top,write_handle,ranks):
	"""This function initiates an html directory file by appending
	the appropriate head tags and css information to create a 
	dynamic tree representation from the directory hierarchy"""
	in_handle = file( os.path.join( top ,'html','folder_initiate.html') ,'r')
	taxcolours = [colour for colour in generate_HEX_colours(len(ranks))]
	line = in_handle.readline()
	while '</head>' not in line:  ### Write everything up to the body tag
		write_handle.write(line)
		line = in_handle.readline()
	write_css( write_handle, ranks ,taxcolours)
	write_handle.write( '\n</head>\n<body>\n' )
	while '<body>' not in line:
		line = in_handle.readline()
	write_key( write_handle, ranks)
	line = in_handle.readline()
	while '<ul' not in line:  # Also get lines up to the start of the taxonomy list.
		write_handle.write(line)
		line = in_handle.readline()
	write_handle.write(line)
	in_handle.close()
	return

def close_html(write_handle):
	"""This function will append the appropriate closing tags to the
	end of the html file"""
	in_handle = file( os.path.join( CONFIG.top ,'html','folder_initiate.html'),'r')
	for line in in_handle.readlines()[45:]:
		write_handle.write(line)
	in_handle.close()
	write_handle.close()
	print "The output html file (%s) has been written and closed" % write_handle.name
	return

def find_start( resultsDict,dbDir = CONFIG.arbDBdir, tdict = CONFIG.taxIndex ):
	nodes = resultsDict.keys()
	if 'accessions' in nodes:
		del(nodes[ nodes.index('accessions') ] )
	nSubs = len(nodes )
	for path,subnode in dict_walk( dbDir,tdict ):
		nfound = 0
		if nodes[0] in subnode.keys():
			nfound += 1
			for node in nodes[1:]:
				if node in subnode.keys():
					nfound += 1
				else:
					nfound = 0
					break
			if nfound == len(nodes):
				return path

def write_key( write_handle, ranks ):
	write_handle.write( '<div style="border: 1px; border-style: solid; right:0; position:absolute;">\n<strong>Key:</strong>')
	for i in xrange(len(ranks)):
	    write_handle.write( '\t<div id="{0}" style="text-align:right;">{0}</div>\n'.format( ranks[i] ) )
	write_handle.write( '</div>' )



if __name__ == '__main__':
	in_name = sys.argv[1]
	sys.stdout.write( 'Loading results File..' )
	sys.stdout.flush()
	if in_name.endswith('.pkl'):
		with file( in_name,'rb') as index_file:
			results = pickle.load( index_file )
		prefix = in_name.rstrip('.pkl')
	else:
		prefix = in_name[:in_name.rfind('.')]
		if not os.path.exists( prefix + '.pkl'):
			print "Need a pickled results file, with extension .pkl"
		with file( prefix + '.pkl','rb') as index_file:
			results = pickle.load(index_file)
	sys.stdout.write( " Done.\n" )
	sys.stdout.flush()
	output_name = prefix + '.htm'
	write_handle = file(output_name,'w')
	sys.stdout.write( 'Loading taxonomic index...' )
	sys.stdout.flush()
	with file( CONFIG.taxIndex,'rb') as handle:
		allNodes = pickle.load( handle )
	sys.stdout.write( ' Done.\n' )
	sys.stdout.flush()
	startDir = find_start( results,dbDir = CONFIG.arbDBdir,tdict = allNodes )
	print 'Found path: {0}'.format(startDir)
	ranks = getAllRanks( results,startDir, CONFIG.mySQLcur )
	initiate_html(CONFIG.top, write_handle,ranks)
	write_html(startDir, write_handle, results)
	close_html(write_handle)
	os.system('chmod 755 {0}'.format(output_name))
