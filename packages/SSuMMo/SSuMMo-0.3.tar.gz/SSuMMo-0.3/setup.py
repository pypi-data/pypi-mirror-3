#!/usr/bin/env python

from sys import platform
from distutils.core import setup 


# There are Windows Binaries available from http://hmmer.janelia.org/software
# ... Wouldn't mind the source code..
# For now, just try and install anyway...

if platform == 'win32':
    platforms = ['win32']
    extra_classifiers = ['Operating System :: Microsoft :: Windows']
#    hmmerdir = os.path.join( 'hmmer-3.0','src' )
#    ext_package = 'hmmer'
#    includes = [ os.path.join( hmmerdir , 'easel' )  ]
#    extensions = []
#    for binary in os.listdir(  hmmerdir ):
#        binary = os.path.join( hmmerdir, binary )
#        if os.path.isfile(binary) and binary.endswith('.c'):
#            extensions.append(  Extension( 'hmmer.{0}'.format(binary.split('.')[0]) , [ hmmerdir+'/'+binary], include_dirs = includes) )
else:
    platforms = ['linux','darwin']
    extra_classifiers = ['Operating System :: MacOS :: MacOS X','Operating System :: POSIX']

extensions = None
ext_package = None

setup( name='SSuMMo',
        version = '0.3',
        description='ssummo. Programs to assign taxonomic info to loads of rRNA sequences.',
        long_description='Library of functions designed around iteratively using hmmer to assign sequences to taxa. Results are highly annotated trees showing species / genus distribution within that community.',
        author='Alex Leach',
        author_email='albl500@york.ac.uk',
        url='http://code.google.com/p/ssummo',
        packages=['ssummo'],
        package_dir = {'ssummo': 'lib' ,
                       'itol':'itol' ,
                       },

        scripts = [ 
            'scripts/dict_to_phyloxml.py' ,
            'scripts/SSUMMO.py' , 
            'scripts/rarefactionCurve.py' , 
            'scripts/rankAbundance.py' , 
            'scripts/ACGTCounts.py' ,
            'scripts/comparative_results.py' ,
            ],

        package_data = { 'ssummo' :  ['html/*'] } , 

        download_url = 'http://code.google.com/p/ssummo/downloads/list',
        platforms = platforms,
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Programming Language :: Python', 
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Topic :: Scientific/Engineering :: Bio-Informatics',
            ] + extra_classifiers,
        ext_package = ext_package,
        ext_modules = extensions

        )


