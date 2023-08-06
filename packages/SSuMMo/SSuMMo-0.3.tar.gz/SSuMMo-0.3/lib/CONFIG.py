"""
This is the configuration file. You are expected to make sure all the
path names and account details in here are right for you!

It is also worth creating an IToL account, requesting a batch-upload
account and entering the username and password they provide into this
file.

***************
Dependencies:-
***************
Make sure that SSuMMo can import the following modules:-
MySQLdb	(from the python-mysql package)
Bio	(the python-biopython package)
  ****
hmmer (at least version 3.0 - available http://hmmer.janelia.org/ )
***************


***************
Compatibility:-
***************
SSUMMO is a package written purely in CPython and has been tested
on Ubuntu & Mac OS X, both running python 2.6.x. & python 2.7.x

IronPython in Windows won't work because it doesn't
allow the use of CPython's built-in 'signal' module. CPython in
windows probably won't work either unless you've got hmmer compiled
and installed and the code relies on /dev/stdin & /dev/stdout, which
are devices only available on *nix operating systems.. The workaround
is to convert sockets bound to localhost into file descriptors.
Any volunteers are welcome! Otherwise, I'll get around to it when I have
time...
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
from sys import platform


#############	MYSQL CONFIGURATION #####################
host = 'localhost'
user = 'username'
passwd = 'mypassword'
### The database 'db' must already exist with the above user
### granted 'all privileges (to create NCBI taxonomy db).
db = 'taxonomies'	

#############	DATA DIRECTORIES ########################
############    WIN
if platform == 'win32':
    top = "C:\\Users\\albl500\\Documents\\PhD\\454RDPstuff\\arbDB"
    blastdir = "C:\\Program Files\\NCBI\\blast-2.2.24+\\bin"

###########    MAC
elif platform == 'darwin':
    #top - directory containing taxIndex
    top = '/path/to/dir'
    #arbDBdir - directory containing HMM database (with Archaea, rArchaea etc.)
    arbDBdir = ' EDIT ME '
    #taxonomic index file (built with dictify.py --indexTaxa)
    taxIndex = 'arbDB104.pkl'
    hmmerdir = ''
    arbdir = ''  
    hmmbuildCmd = 'hmmbuild'
    hmmsearchCMD = 'hmmsearch'
    VxtractorDir =  top+ '/vxtractor' 
#############   UBUNTU
elif platform == 'linux2':
    top = '/var/lib/ssummo'
    arbDBdir = '/var/lib/ssummo/arbDB104'
    hmmerdir = ''	## Only hmmer version 3 and above are supported.
    arbdir = ''  	## Directory where ARB's bin & lib directories etc are. (deprecated)
    blastversion = '2.6'
    taxIndex = 'arbDB104.pkl'
    hmmbuildCMD = 'hmmbuild'
    hmmsearchCMD = 'hmmsearch'
    VxtractorDir =  top + '/vxtractor'
    hmmalignCMD = 'hmmalign'
############## CUSTOM COMMANDS ###############


######## ITOL info ########

itolID = 'Get an ID from http://itol.embl.de'
itolProject = 'myproject'


############################ LEAVE ########################################
options = None # Leave this... Initiates the CONFIG.options namespace. ####
