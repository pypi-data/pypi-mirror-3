from fileTools import *

class Rule( object ):
   def __init__( self, target, dependancies, action, description=None ):
      global TARGET, NEEDS

      self._target       = target
      self._description  = description
      self._dependancies = { }           # dependency to rule
      self._action       = None

      TARGET = self._target
      NEEDS  = [ ]
      for dependancy in dependancies:
         NEEDS.append( self.expandMacros(dependancy) )

      for dependancy in NEEDS:
         self._dependancies[ dependancy ] = None

      self._action = self.expandMacros( action )

   def getDependancies( self ):
      return self._dependancies.keys( )

   def getDescription( self ):
      return self._description

   def defineDependencyRule( self, dependencyName, Rule ):
      self._dependancies[ dependencyName ] = Rule

   def build( self ):
      target = os.path.normpath( self._target )

      # Handle subrules
      if len( self._dependancies ) == 0:
         needToRebuildTarget = True
      else:
         needToRebuildTarget = not os.path.exists( target )

      for dependency, subrule in self._dependancies.iteritems( ):
         dependency = os.path.normpath( dependency )
         if not os.path.exists( dependency ):
            if subrule:
               subrule.build( )
               print '-----------------------------------'
            else:
               raise Exception( 'No rule to build target %s' % dependency )

         if os.path.exists( target ):
            targetTime     = os.stat( target ).st_mtime
            dependencyTime = os.stat( dependency ).st_mtime

            if dependencyTime > targetTime:
               needToRebuildTarget = True

      if needToRebuildTarget:
         print 'Building: %s' % target
         execActionCode( self._action )

   def expandMacros( self, aString ):
      macroStart = aString.find( '${' )

      while macroStart != -1:
         macroEnd   = aString.find( '}', macroStart+2 )
         macroSeq   = aString[ macroStart+2 : macroEnd ].split( ',' )

         if '.' in macroSeq[0]:
            var,op = macroSeq[0].split('.')
         else:
            var = macroSeq[0]
            op  = None

         value = globals( )[ var ]

         if isinstance( value, (str,unicode) ):
            if op == 'dir':
               value = os.path.dirname( value )
            elif op == 'name':
               value = os.path.basename( value )
            elif op == 'base':
               value = os.path.splitext( os.path.basename( value ) )[0]
            elif op == 'ext':
               value = os.path.splitext( os.path.basename( value ) )[1]

            if len(macroSeq) > 1:
               mark = macroSeq[1].find( '=' )
               if mark == -1:
                  raise Exception( 'Error in macro' )
               old = macroSeq[1][ : mark  ]
               new = macroSeq[1][ mark+1 : ]
               value = value.replace( old, new )

            aString = aString[ :macroStart ] + value + aString[ macroEnd+1: ]
            macroStart = aString.find( '${' )
         elif isinstance( value, (list,tuple) ):
            pass

      return aString

class Builder( object ):
   def __init__( self, projectName='' ):
      self._rules           = { }
      self._topLevelTargets = [ ]
      self._allTargets      = [ ]
      self._leaves          = [ ]
      self._projectName     = projectName
      self._menuOrder       = [ ]

   def addTarget( self, targets, *args ):
      if isinstance( targets, str ):
         targets = [ targets ]

      numArgs = len( args )

      if numArgs == 3:
         # We have a description
         description  = args[0]
         dependencies = args[1]
         actions      = args[2]
      elif numArgs == 2:
         # No description
         description  = None
         dependencies = args[0]
         actions      = args[1]
      else:
         raise TypeError( 'addTarget() takes 3 or 4 arguments (%d given)' % numArgs )

      for target in targets:
         depend = [ ]

         self._rules[ target ] = Rule( target, dependencies, actions, description )
         self._menuOrder.append( target )

   def finalize( self ):
      # Assemble the Rules into a Tree
      for target, rule in self._rules.iteritems( ):
         for dependencyName in rule.getDependancies( ):
            if dependencyName in self._rules:
               rule.defineDependencyRule( dependencyName, self._rules[ dependencyName ] )
            else:
               if dependencyName not in self._leaves:
                  self._leaves.append( dependencyName )

      # Determine the top-level targets
      targets = self._rules.keys( )

      for name in self._rules.keys( ):
         for rule in self._rules.values( ):
            if name in rule.getDependancies( ):
               if name in targets:
                  targets.remove( name )

      targets.sort()
      self._topLevelTargets = [ ]
      for targetName in self._menuOrder:
         if targetName in targets:
            self._topLevelTargets.append( ( targetName, self._rules[ targetName ].getDescription() ) )
      
      # Create the allTargets list
      self._allTargets = [ ]
      for targetName in self._menuOrder:
         descr = self._rules[ targetName ].getDescription()
         if descr is not None:
            self._allTargets.append( ( targetName, descr ) )
         else:
            self._allTargets.append( ( targetName, ''    ) )

   def targets( self ):
      return self._rules.keys( )

   def build( self, target ):
      print '********** Building Target: %s...' % target

      try:
         theRule = self._rules[ target ]
         theRule.build( )
         print '********** Build completed.'
      except:
         type,value,trace = sys.exc_info( )
         print 'BUILD FAILED!!!'
         print traceback.print_exc( )

   def topTargets( self ):
      return self._topLevelTargets

   def allTargets( self ):
      return self._rules.keys( )

   def initializationCode( self, code ):
      execActionCode( code )

   def goInteractive( self ):
      print
      print 'Entering Interactive Builder'

      response = ''
      self._buildMenu( self._topLevelTargets )
      while response != 'exit':
         target = raw_input( '\nbuild> ' )

         if target == 'showall':
            self._buildMenu( self._allTargets )
            continue
         elif target == 'exit':
            break
         elif target in self.allTargets( ):
            print
            print
            self.build( target )
            self._buildMenu( self._topLevelTargets )
         else:
            print '   !!! Unknown Target !!!'

   def _buildMenu( self, targetList ):
      print
      print 'Targets:'
      for targetName, targetDescription in targetList:
         if targetDescription:
            print '   %-20s  %s' % ( targetName, targetDescription )
         else:
            print '   %-20s' % ( targetName )

      print
      print '   %-20s  %s' % ( 'showall', 'Show the full list of targets.' )
      print '   %-20s  %s' % ( 'exit',    'Exit the interactive builder.'  )


bld = Builder( )


def buildTarget( aTargetName ):
   bld.build( aTargetName )

def execActionCode( code ):
   exec code in globals( )
