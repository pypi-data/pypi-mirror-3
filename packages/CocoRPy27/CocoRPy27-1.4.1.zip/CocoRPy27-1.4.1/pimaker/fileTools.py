import os
import os.path
import fnmatch
from glob import glob
import difflib
import sys
import traceback
import shutil
import time


LAUNCH_DIR = os.getcwd( )
ROOT_DIR = os.path.dirname( __file__ )
os.chdir( ROOT_DIR )

TARGET = ''
NEEDS  = [ ]

def expandGlob( aPathPattern ):
   '''Given a pathname pattern, return a list of all the paths on
   the local filesystem that match the pattern.'''
   return glob( os.path.normpath( aPathPattern ) )

def expandGlobList( paths ):
   '''Given a list of pathname patterns, return a list of all the
   paths on the local filesystem that match the patterns.

   paths may be:
      pathname as string
      pathname pattern as string
      pathname list as a string of ; separated patterns - not implemented
      pathname list who elements may be pathname or pathname pattern.
   returns:
      A list of all the paths on the local filesystem that match the
      patterns.
   '''
   if isinstance( paths, str ):
      return expandGlob( paths )
   elif isinstance( paths, (list,tuple) ):
      result = [ ]
      for pattern in paths:
         result += expandGlob( pattern )
      return result
   else:
      raise Exception( 'invalid argument type' )

def splitStringList( aString ):
   '''Given a string representing a list of glob, return a python
   list of glob.
   '''
   def strip( val ):
      return val.strip( )

   lst = aString.split( ';' )
   lst = map( strip, lst )

   return lst

def splitLists( *lists ):
   '''Given a list of things that may be a mix of globs or globlists,
   return a single python list of globs.

   items passsed may be:
      pathname or glob as string
      a list as a string containing pathname or glob all separated by ;
      a python list of pathname, glob or a list as a string of pathname or glob separated by ;
   '''
   result = [ ]

   for lst in lists:
      if isinstance( lst, str ):
         result += splitStringList( lst )
      elif isinstance( lst, (list,tuple) ):
         for elt in lst:
            result += splitStringList( elt )

   return result

def renameFile( filename, filename2 ):
   return os.renames( os.path.normpath(filename), os.path.normpath(filename2) )

def makeDirs( *dirNames ):
   dirNames = splitLists( *dirNames )
   for dirName in dirNames:
      dirName = os.path.normpath(dirName)
      if not os.path.exists( dirName ):
         os.makedirs( dirName )
      elif not os.path.isdir( dirName ):
         Exception( "Can't MakeDir.  Name already exists as a file. (%s)" % dirName )

def moveFilesTo( destDir, *paths ):
   '''Move the files named by paths to dirname.  Overwrite existing files.'''
   paths = splitLists( *paths )

   normDir = os.path.normpath( destDir )
   MakeDir( normDir )

   for name in expandGlobList( paths ):
      normName= os.path.normpath( name )
      base = os.path.basename( normName )
      dest = normDir + '/' + base
      os.renames( normName, normDir )

def copyFilesTo( destDir, *paths ):
   '''Copy the files named by paths to dirname.  Overwrite existing files.'''
   normDir = os.path.normpath( destDir )
   if not os.path.exists( normDir ):
      makeDirs( normDir )

   paths = splitLists( *paths )
   for filename in expandGlobList( paths ):
      normFilename = os.path.normpath( filename )
      if os.path.isdir( normFilename ):
         shutil.copytree( normFilename, normDir )
      else:
         shutil.copy2( normFilename, normDir )

def deleteFiles( *paths ):
   paths = splitLists( *paths )
   for name in expandGlobList( paths ):
      normName = os.path.normpath(name)
      if os.path.exists( normName ):
         if os.path.isdir( normName ):
            shutil.rmtree( normName )
         else:
            os.remove( normName )

def changeDir( destDir ):
   os.chdir( os.path.normpath(destDir) )

def compareFiles( fn1, fn2, **kwds ):
   '''Options:
         ignoreHeader=<numLinesToIgnore>
            Ignore the first n lines of both input files.
   '''
   f1 = file( os.path.normpath(fn1), 'r' ).readlines( )
   f2 = file( os.path.normpath(fn2), 'r' ).readlines( )

   if 'ignoreHeader' in kwds:
      numLinesToIgnore = kwds[ 'ignoreHeader' ]
      return list(difflib.context_diff( f1[ numLinesToIgnore: ], f2[ numLinesToIgnore: ] ))
   else:
      return list(difflib.context_diff( f1, f2 ))

def genHTMLDiff( fromFile, toFile, htmlDiffFilename ):
   fromLines = open( os.path.normpath(fromFile), 'U' ).readlines( )
   toLines   = open( os.path.normpath(toFile),   'U' ).readlines( )
   
   diff = difflib.HtmlDiff().make_file( fromLines, toLines, fromFile, toFile )
   
   out = file( htmlDiffFilename, 'w' )
   out.write( diff )
   
def dos2unix( filename ):
   if isinstance( filename, str ):
      fName = [ filename ]
   else:
      fName = filename

   for fname in fName:
      infile = open( fname, "rb" )
      instr = infile.read()
      infile.close()
      outstr = instr.replace( "\r\n", "\n" ).replace( "\r", "\n" )

      if len(outstr) == len(instr):
         continue

      outfile = open( fname, "wb" )
      outfile.write( outstr )
      outfile.close()

def unix2dos( filename ):
   if isinstance( filename, str ):
      fName = [ filename ]
   else:
      fName = filename

   for fname in fName:
      infile = open( fname, "rb" )
      instr = infile.read()
      infile.close()
      outstr = instr.replace( "\n", "\r\n" )

      if len(outstr) == len(instr):
         continue

      outfile = open( fname, "wb" )
      outfile.write( outstr )
      outfile.close()

def touch( filename ):
   os.utime( filename )

def shell( *strings ):
   command = ' '.join( strings )
   os.system( command )


