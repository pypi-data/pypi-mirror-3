'''
CocoR_Tester executes Coco/R on an atg file and determines pass/fail by
comparing the output to previously know correct output.  A single execution of
Coco/R may produce up to five different output files: Scanner.py, Parser.py,
trace.txt, a driver file, and output to stdout (the screen) which CocoR_Tester
will redirect into a file for conducting the test.

The file against which each of the five outputs is compared is called a
baseline.  The names of the baselines follw the conventions here:

   stdout            <ATGfilename>_stdoutBaseline.txt
   trace             <ATGfilename>_traceBaseline.txt
   scanner           <ATGfilename>_scannerBaseline.py
   parser            <ATGfilename>_parserBaseline.py
   driver            <ATGfilename>_driverBaseline.py

Baseline files must reside in the same directory as the atg being tested.

A test suite consists of a list of specifications for tests to be performed in
the order in which they appear in the list.  A test specification is a tuple
having the following format.

( ATGfilename, cocoFlags, testList )

ATGFilename
   Is the filename of the atg file (without a path or the .atg extension).
   All atg files must be in the current directory (os.getcwd())

cocoFlags
   Any flags passed to coco to compile ATGFilename.  These flags must
   direct coco to produce the appropriate files to be able to perform the tests
   specified by testList.

testList
   A tuple of five values, one for each of the five things that Coco/R is
   capable of outputting.

   ( stdout, traceFile, GeneratedScanner, GeneratedParser, GeneratedDriver )

   For each position, the following values are possible for these fields.

   'skip'
      Don't test this.  Generally not reccomended to skip the stdout test.

   'absent'
      Verify that the Coco/R did NOT produce any output for this item.
      'absent' only applies to Scanner, Parser and Driver generation.

   'exist'
      Verify only that the process of executing Coco/R produced a file and that
      the file is non-empty.  'exist' only applies for trace, scanner, parser
      and driver.
      
   'dif'
      Compare the output against the baseline file.
'''

import os

from fileTools import *

class CocoR_Tester( object ):
   def __init__( self, cocoExec ):
      self._cocoExec    = cocoExec

   def compileBaselines( self, atgFilename, cocoFlags ):
      testStdoutOutput, testTraceOutput, testGeneratedScanner, testGeneratedParser, testGeneratedDriver = testList
      print 'Compiling baseline files for test: %s' % atgFilename

      if not atgFilename.lower().endswith( '.atg' ):
         baseName = atgFilename
         atgFilename += '.atg'
      else:
         baseName = os.path.splitext( os.path.basename( atgFilename ) )[0]

      if not os.path.exists( atgFilename ):
         raise 'ATG file not found %s' % atgFilename

      shell( '%s %s > %s_stdoutBaseline.txt' % (self._cocoExec, atgFilename, baseName) )
      deleteFiles( '%s_Trace.txt' % baseName, '%s_Parser.py' % baseName, '%s_Scanner.py' % baseName )
      renameFile( 'trace.txt',  '%s_traceBaseline.txt'  % baseName )

      if not isErrorBase:
         renameFile( 'Parser.py',      '%s_parser.py'         % baseName )
         renameFile( 'Scanner.py',     '%s_scanner.py'        % baseName )
         renameFile( baseName + '.py', '%s_driverBaseline.py' % baseName )

   def compileAllBaselines( self, aSuite ):
      '''build the baseline files.
      Note:  This will overwrite existing files.'''
      for name,cocoFlags,testList in aSuite:
         self.compileBases( name,cocoFlags )

      print 'Done.'

   def performExistTest( self, outputFilename ):
      '''Return True if the file exists and has a file size > 0, False otherwise.'''
      if not os.path.exists( outputFilename ):
         return False
      
      return os.stat( outputFilename ) > 0

   def performAbsentTest( self, outputFilename ):
      '''Return True if the file is absent, False otherwise.'''
      return not os.path.exists( outputFilename )

   def performDifTest( self, outputFilename, baselineFilename, **compareOptions ):
      '''Return True if the files are identical, False otherwise.'''
      try:
         result = compareFiles( outputFilename, baselineFilename, **compareOptions )
         return len(result) == 0
      except:
         return False

   def test( self, testType, outputFilename, baselineFilename, **options ):
      if testType == 'dif':
         if not self.performDifTest( outputFilename, baselineFilename, **options ):
            print '   - PROBLEM: %s differs from baseline.' % ( outputFilename )
            return False
      elif testType == 'absent':
         if not self.performAbsentTest( outputFilename ):
            print '   - PROBLEM: %s should have not been generated.' % ( outputFilename )
            return False
      elif testType == 'exist':
         if not self.performExistTest( outputFilename ):
            print '   - PROBLEM: %s was not generated.' % ( outputFilename )
            return False
      
      return True

   def check( self, name, cocoFlags, *testList ):
      print 'Running test: %s' % name
      stdoutTest, traceTest, scannerGenTest, parserGenTest, driverGenTest = testList

      # Setup
      if (len(cocoFlags) > 0) and (cocoFlags[0] != '-'):
         cocoFlags = '-' + cocoFlags
      shell( '%s %s %s.atg >stdout.txt' % (self._cocoExec, cocoFlags, name) )
      
      # Run Tests
      success = True
      
      success = success and self.test( stdoutTest,     'stdout.txt',  name + '_stdoutBaseline.txt', ignoreHeader=1 )
      success = success and self.test( traceTest,      'trace.txt',   name + '_traceBaseline.txt'  )
      success = success and self.test( scannerGenTest, 'Scanner.py',  name + '_scannerBaseline.py' )
      success = success and self.test( parserGenTest,  'Parser.py',   name + '_parserBaseline.py'  )
      success = success and self.test( driverGenTest,   name + '.py', name + '_driverBaseline.py'  )
   
      # Clean Up
      deleteFiles( '*.py.old', 'Parser.py', 'Scanner.py', 'output.txt', 'trace.txt' )

      return success

   def checkAll( self, aSuite ):
      numFailures = 0

      for name,cocoFlags,testList in aSuite:
         passed = self.check( name, cocoFlags, *testList )
         if not passed:
            numFailures += 1

      print '%d failures out of %d tests.' % ( numFailures, len(aSuite) )

if __name__ == '__main__':
   changeDir( '..' )
   COCORoot = os.getcwd()
   sys.path.append( COCORoot )
   changeDir( 'testSuite' )
   
   import CocoR_Tester
   from testSuite.testSuiteInfo import suite as testSuite_testList

   theTester = CocoR_Tester.CocoR_Tester( 'python ' + os.path.join(COCORoot, 'Coco.py') )
   theTester.checkAll( testSuite_testList )
