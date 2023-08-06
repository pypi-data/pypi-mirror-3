Coco/R (http://ssw.jku.at/coco/) is a compiler generator, which takes an
attributed grammar of a source language and generates a scanner and a parser
for this language. The scanner works as a deterministic finite automaton.
The parser uses recursive descent. LL(1) conflicts can be resolved by a
multi-symbol lookahead or by semantic checks. Thus the class of accepted
grammars is LL(k) for an arbitrary k.

There is version of Coco/R for Python language.

This is a fork of CocoPy-1.1.0rc (http://pypi.python.org/pypi/CocoPy/) of
Ronald Longo aixp/cocopy merged back into my original repository.


!!!PLEASE NOTE!!!
This distribution is a release candidate.

SETUP AND USAGE
===============
Setup and usage information can be found in section 3 of
documentation/CocoDoc.htm.  CocoDoc.htm contains everything you need to
use Coco for Python.

QUICKSTART - Test the installation
==================================
1.  Insure that python 2.7 is the default python.  You can do this by
    entering the following command at a shell or dos box prompt:

          'python -V' <-- capital 'V'.

2.  Unzip the CocoRPy27 into some convenient location.

3.  CD into the CocoRPy27 folder structure.

4.  CD into the pimaker subfolder.

    PIMaker (Python Interactive Make utility) is a program/mini-language that
    I wrote and have included in the Coco/R distribution as a practical example
    of using Coco/R.  PIMaker is used in Coco/R to perform routine tasks with
    the dsitribution.  It behaves very much like 'make'.

5.  To be able to use pimaker, it's grammar must be compiled using Coco/R.
    Execute the following command to compile pimaker and generate the pimaker
    python application code

          'python ../coco.py -c pimaker.atg'

6.  You should get 0 errors.  To insure that pimaker.py was generated
    correctly by Coco/R, execut the following command:

          'python pimaker.py' to insure that pimaker compiled.

    If Coco/R successfully compiled PIMaker and generated pimaker.py, it
    will read in and parse the makepi.how file (written in PIMaker's language).
    Pimaker will then present you with a menu of 'Targets:' it found in the
    makepi.how file, and present you with a 'build>' prompt.

7.  Testing.  There are several tests that this pimaker script can perform.
    First the general functionality of Coco/R to insure that it contains no
    bugs in the primary logic.  Do this by entering 'testFunctions' at the
    pimaker prompt.  When the tests complete, the message '0 tests failed.'
    should be printed.  Then you should be returned to the list of Targets and
    build prompt.  Now type 'testExamples' to compile the example grammars.
    Some of the grammars intensionally have errors or are non-LL(k).
    
    Type 'exit'.  Congratulation!  Coco/R is now installed and ready for use.
    Please refer to the Documentation subfolder to learn how to construct
    compilers and parsers using Coco/R.
    
    Note:  I reccomend against executing any of the remaining targets in pimaker
    until you understand what they will do.

CONTENTS OF THIS DISTRIBUTION
=============================
This file contains a list of the contents of the distribution and a
development roadmap.

This distribution of Coco includes the following:

   Coco root directory

      The application files

      Coco.py            - The main application file
      Scanner.py         - The lexical analizer for attributed grammars
      Parser.py          - The parser for attributed grammars

      DriverGen.py       - Generates the main application
      ParserGen.py       - Generates the parser
      CodeGenerator.py   - Common code generation routines
      CharClass.py       - Implementation of character classes
      Errors.py          - Tracking and reporting errors in the source grammar
      Trace.py           - Routines for generating trace files
      Core.py            - Scanner generator and various support classes.

      Other

      setup.py           - Python distribution utilities setup script for Coco.
      setupInfo.py       - CocoPy Version information
      README.txt         - this file.

   /documentation

      license.txt        - The license agreement
      CocoDoc.htm        - The documentation for CocoPy
      howToBootstrap.txt - Instructions on how to bootstrap Coco (outdated)
      DataStructurres.pdf- A description of the workings of Coco
      pimaker.txt        - Documentation of pimaker.

   /examples

      Various example Attributed Grammars, not all are LL(1).

   /frames

      The basic Frame files.  These are template files used by the code
      generation routines.

   /sources

      These are the source files needed to bootstrap CocoPy.

      Coco.atg       - The grammar for the Coco language.
      Coco.frame     - Frame file for Coco's main module.
      Parser.frame   - Frame file for Coco's parser module.
      Scanner.frame  - Frame file for Coco's scanner module.

   /pimaker (Python Interactive Make utility)

      The Python Interactive Make utility written in Coco as a practical
      example of Coco usage.

      pimaker.atg    - The grammar for a makepi.how file.
      pimaker.frame  - The frame file for pimaker's main module.
      pimakerlib.py  - Library of routines needed by pimaker.
      makepi.how     - Pimaker's equivalent to a 'makefile' to bootstrap Coco.

   /testSuite

      The testbootstrap target in pimaker simply diffs the generated files
      coco.py, Parser.py and Scanner.py.  If there are no differences,
      the test passes.  However, when modifications are made to Coco.py
      this sort of testing is not sufficient.

      The suite of tests is in this directory are ported for the C#
      implementation of Coco/R.  They test Coco/R features.  To run the
      test suite open a command shell into the testSuite folder and execute
      the following:

         >>> python cocopTester.py


ROADMAP
=======

   - Version numbering is tentative.


Release#   Goal
--------   ------------------------------------------------------
3.0        Updated to Python 3.x

2.0        Updated for consistency to the latest reference
           implementations (Java & C#).

1.9        Initial release of Coco/R for Python updated to the reference
           implementations.

1.5        Full well tested release AIXP's fork merged back into my code base.

1.4        New release... AIXP's fork of my original Python port merged back
           into my code base.

1.0.10b2.  Coco now bootstraps correctly.

1.1.0rc.   *** Release Candidate -- Coco now successfully runs the test suite
           from the C# implementation.

1.1.1rc.   Coco now correctly parses the examples and reports all the errors
           in the example grammars.

1.1.2rc.   Code generated from examples now sucessfully loads into python
           using 'python name.py'

1.1.3rc    Code generated from examples now successfully parses input
           and generates errors when appropriate.

1.4.0      First release after merging the aixp/coco fork back into Ron Longo's
           original implementation of Coco/R for Python.

1.5.0      Release of Coco/R brought into alignment with the Java and C#
           reference implementations.

2.0.0.     Coco/R for Python 3.x


