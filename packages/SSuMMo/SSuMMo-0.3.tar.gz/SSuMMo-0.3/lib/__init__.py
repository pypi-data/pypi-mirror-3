print """SSUMMO Copyright (C) 2011. Alex Leach, University of York.
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions; see the file COPYING for details.."""

import os,sys
ssummo_working_directory = os.path.realpath( __file__ ).rsplit( os.path.sep , 1 )[0]
sys.path.insert( 0 , ssummo_working_directory )

