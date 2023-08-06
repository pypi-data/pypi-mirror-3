import time


MetaData = {
   'name':             'CocoRPy27',
   'long_name':        'Coco/R for Python 2.7',
   'version':          '1.4.1',
   'build_date':       time.strftime( '%Y-%m-%d %H:%M:%S GMT', time.gmtime() ),
   'description':      'Python implementation of the famous CoCo/R LL(k) compiler generator ported to Python.',
   'url':              'https://sourceforge.net/projects/cocorforpython/',
   'download_url':     'https://sourceforge.net/projects/cocorforpython/',
   'Coco/R URL':       'http://www.ssw.uni-linz.ac.at/coco',
   'author':           'Ronald H Longo',
   'author_email':     'ron_longo@verizon.net',
   'maintainer':       'Ronald H Longo',
   'maintainer_email': 'ron_longo@verizon.net',
   'platforms':        [ 'Python 2.7', 'Windows', 'Unix' ],
   'license':          'GPL',
   'packages':     [ '' ],
   'data_files':   [
                   ( 'documentation', [ 'documentation/*' ] ),
                   ( 'examples',      [ 'examples/*'      ] ),
                   ( 'frames',        [ 'frames/*'        ] ),
                   ( 'pimaker',       [ 'pimaker/*'       ] ),
                   ( 'sources',       [ 'sources/*'       ] ),
                   ( 'testSuite',     [ 'testSuite/*'     ] )
                   ],
   'classifiers':  [
                   'Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'Intended Audience :: Education',
                   'Intended Audience :: Information Technology',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Natural Language :: English',
                   'Programming Language :: Python',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Scientific/Engineering :: Human Machine Interfaces',
                   'Topic :: Scientific/Engineering :: Information Analysis',
                   'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
                   'Topic :: Software Development :: Code Generators',
                   'Topic :: Software Development :: Compilers',
                   'Topic :: Software Development :: Interpreters',
                   'Topic :: Software Development :: Pre-processors',
                   'Topic :: System :: Shells',
                   'Topic :: Text Processing :: General',
                   'Topic :: Text Processing :: Linguistic'
                   ]
   }

VersionInfo = {
   '1.4':
      {
      'changes':       [ "Branch from git/aixp, merged into Ron Longo's original main line.",
                         "Pimaker version 1.1" ],
      'bugfixes':      [ "several file loading and path problems" ],
      'contributions': [ 'Ron Longo performed the merge.' ]
      },
   
   '1.2aixp': {
      'changes':       [ "Branch from Ron Longo's original implementation to git/aixp." ],
      'bugfixes':      [ "few" ],
      'contributions': [ "git/aixp, the latest updates from the java implementation." ]
      },
      
   '1.1.0rc': {
      'changes':       [ "Coco/R now passes all tests of the official Coco/R test suite" ],
      'bugfixes':      [ ],
      'contirubtions': [ ]
      },

   '1.0.10b2':{
      'changes':       [ "Updated builder and renamed it to pimaker" ],
      'bugfixes':      [ "Many code generator bug fixes" ],
      'contributions': [ "Wayne Wiitanen has contributed a version of the EXPR example that works with CocoPy." ]
      },

   '1.0.9b2': {
      'changes':       [ "Simplified the Errors class and error handling.",
                         "Completed a first version of my builder application." ],
      'bugfixes':      [ "Repaired a bug in SemErr() didn't work properly." ]
      },

   '1.0.7b1': {
      'changes':       [ ],
      'bugfixes':      [ "Repaired LINUX bug found in v1.0.6b1" ]
      },

   '1.0.6b1': {
      'changes':       [ "Completed a beta version of builder.py",
                         "Updated README.txt to describe builder.py",
                         "Removed HowToBootstrap.txt from Documents" ],
      'bugfixes':      [ "Coco.atg does not bootstrap on LINUX." ]
      }
   }
