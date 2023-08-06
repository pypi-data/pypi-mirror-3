# Note:  Compile flags are included as pragmas within each testsuite file.

SKIP   =  'skip'
DIF    =  'dif'
ABSENT =  'absent'

info = [
   # ATG name             COCO   ( Tests:                                 )
   #                      FLAGS  ( stdout, Trace, Scanner, Parser, Driver )
   ('TestAlts',           '',    ( DIF,    DIF,   DIF,     DIF,    ABSENT )),
   ('TestOpts',           '',    ( DIF,    DIF,   DIF,     DIF,    ABSENT )),
   ('TestOpts1',          '',    ( DIF,    DIF,   DIF,     DIF,    ABSENT )),
   ('TestIters',          '',    ( DIF,    DIF,   DIF,     DIF,    ABSENT )),
   ('TestEps',            '',    ( DIF,    DIF,   DIF,     DIF,    ABSENT )),
   ('TestAny',            '',    ( DIF,    DIF,   DIF,     DIF,    ABSENT )),
   ('TestAny1',           '',    ( DIF,    DIF,   DIF,     DIF,    ABSENT )),
   ('TestSync',           '',    ( DIF,    DIF,   DIF,     DIF,    ABSENT )),
   ('TestSem',            '',    ( DIF,    DIF,   DIF,     DIF,    ABSENT )),
   ('TestWeak',           '',    ( DIF,    DIF,   DIF,     DIF,    ABSENT )),
   ('TestChars',          '',    ( DIF,    DIF,   DIF,     DIF,    ABSENT )),
   ('TestTokens',         '',    ( DIF,    DIF,   DIF,     DIF,    ABSENT )),
   ('TestTokens1',        '',    ( DIF,    DIF,   ABSENT,  ABSENT, ABSENT )),
   ('TestComments',       '',    ( DIF,    DIF,   DIF,     DIF,    ABSENT )),
   ('TestDel',            '',    ( DIF,    DIF,   DIF,     DIF,    ABSENT )),
   ('TestTerminalizable', '',    ( DIF,    DIF,   ABSENT,  ABSENT, ABSENT )),
   ('TestComplete',       '',    ( DIF,    DIF,   ABSENT,  ABSENT, ABSENT )),
   ('TestReached',        '',    ( DIF,    DIF,   ABSENT,  ABSENT, ABSENT )),
   ('TestCircular',       '',    ( DIF,    DIF,   ABSENT,  ABSENT, ABSENT )),
   ('TestLL1',            '',    ( DIF,    DIF,   DIF,     DIF,    ABSENT )),
   ('TestResOK',          '',    ( DIF,    DIF,   DIF,     DIF,    ABSENT )),
   ('TestResIllegal',     '',    ( DIF,    DIF,   ABSENT,  ABSENT, ABSENT )),
   ('TestCasing',         '',    ( DIF,    DIF,   DIF,     DIF,    ABSENT ))
   ]


