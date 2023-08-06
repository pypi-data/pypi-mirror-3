import os
import os.path
import fnmatch
from glob import glob
import difflib
import sys
import traceback
import shutil

# Let's add the COCO root directory to the Python Path
# So that we can import modules from other folders in the project.
workingDir = os.getcwd()
os.chdir( '..' )
COCORoot = os.getcwd()

sys.path.append( COCORoot )
from pimaker.fileTools import *

os.chdir( COCORoot )
os.chdir( 'testSuite' )        # Force to the testSuite dir!


class CocoTester( object ):
   def __init__( self, compiler, targetLanguageExt, testSuite ):
      self._compiler    = compiler
      self._fnTgtExt    = targetLanguageExt
      self._suite       = testSuite

   def compileBases( self, atgFilename,isErrorBase=False ):
      '''Python replacement for compile.bat.'''
      print 'Compiling bases for test: %s' % atgFilename

      if not atgFilename.lower().endswith( '.atg' ):
         baseName = atgFilename
         atgFilename += '.atg'
      else:
         baseName = os.path.splitext( os.path.basename( atgFilename ) )[0]

      if not os.path.exists( atgFilename ):
         raise 'ATG file not found %s' % atgFilename

      shell( '%s %s > %s_Output.txt' % (self._compiler, atgFilename, baseName) )
      deleteFiles( '%s_Trace.txt' % baseName, '%s_Parser.py' % baseName, '%s_Scanner.py' % baseName )
      renameFile( 'trace.txt',  '%s_Trace.txt'  % baseName )

      if not isErrorBase:
         renameFile( 'Parser.py',  '%s_Parser.py'  % baseName )
         renameFile( 'Scanner.py', '%s_Scanner.py' % baseName )

   def compileAllBases( self ):
      '''Python replacement for compileall.bat.'''
      for name,testType in self._suite:
         self.compileBases( name,testType )

      print 'Done.'

   def check( self, name, isErrorTest=False ):
      print 'Running test: %s' % name

      shell( '%s %s.atg >output.txt' % (self._compiler, name) )
      if compareFiles( 'trace.txt', '%s_Trace.txt' % name ):
         print 'trace files differ for %s' % name
         return False
      if compareFiles( 'output.txt', '%s_Output.txt' % name, ignoreHeader=1 ):
         print 'output files differ for %s' % name
         return False

      if not isErrorTest:
         if compareFiles( 'Parser.py', '%s_Parser.py' % name ):
            print 'output files differ for %s' % name
            return False
         if compareFiles( 'Scanner.py', '%s_Scanner.py' % name ):
            print 'output files differ for %s' % name
            return False

      deleteFiles( '*.py.old', 'Parser.py', 'Scanner.py', 'output.txt', 'trace.txt' )

      return True

   def checkall( self ):
      numFailures = 0

      for name,isErrorTest in self._suite:
         passed = self.check( name, isErrorTest )
         if not passed:
            numFailures += 1

      print '%d tests failed.' % numFailures
      print 'Done.'

suite = [
      ( 'TestAlts',           False ),
      ( 'TestOpts',           False ),
      ( 'TestOpts1',          False ),
      ( 'TestIters',          False ),
      ( 'TestEps',            False ),
      ( 'TestAny',            False ),
      ( 'TestAny1',           False ),
      ( 'TestSync',           False ),
      ( 'TestSem',            False ),
      ( 'TestWeak',           False ),
      ( 'TestChars',          False ),
      ( 'TestTokens',         False ),
      ( 'TestTokens1',        True  ),
      ( 'TestComments',       False ),
      ( 'TestDel',            False ),
      ( 'TestTerminalizable', True  ),
      ( 'TestComplete',       True  ),
      ( 'TestReached',        True  ),
      ( 'TestCircular',       True  ),
      ( 'TestLL1',            False ),
      ( 'TestResOK',          False ),
      ( 'TestResIllegal',     True  ),
      ( 'TestCasing',         False )
      ]

tester = CocoTester( 'python ../Coco.py', 'py', suite )
tester.checkall( )
