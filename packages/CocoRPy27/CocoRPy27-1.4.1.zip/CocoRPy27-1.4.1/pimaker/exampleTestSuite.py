# Note:  Compile flags are included as pragmas within each testsuite file.

SKIP   =  'skip'
EXIST  =  'exist'
ABSENT =  'absent'
DIF    =  'dif'

info = [
   # ATG name,            COCO,  ( Tests: 'dif', 'absent', 'skip'         )
   #                      FLAGS  ( stdout, Trace, Scanner, Parser, Driver )
   ('AdaCS',              '-cn', ( SKIP,   SKIP,  EXIST,   EXIST,  EXIST  ) ),
   ('C',                  '-cn', ( SKIP,   SKIP,  EXIST,   EXIST,  EXIST  ) ),
   ('CDecl1',             '-cn', ( SKIP,   SKIP,  EXIST,   EXIST,  EXIST  ) ),
   ('CDecl2',             '-cn', ( SKIP,   SKIP,  EXIST,   EXIST,  EXIST  ) ),
   ('CDecl3',             '-cn', ( SKIP,   SKIP,  EXIST,   EXIST,  EXIST  ) ),
   ('CLang1',             '-cn', ( SKIP,   SKIP,  EXIST,   EXIST,  EXIST  ) ),
   ('CLang2',             '-cn', ( SKIP,   SKIP,  EXIST,   EXIST,  EXIST  ) ),
   ('Expr',               '-cn', ( SKIP,   SKIP,  EXIST,   EXIST,  EXIST  ) ),
   ('MicroAda',           '-cn', ( SKIP,   SKIP,  EXIST,   EXIST,  EXIST  ) ),
   ('Mod2',               '-cn', ( SKIP,   SKIP,  EXIST,   EXIST,  EXIST  ) ),
   ('Oberon',             '-cn', ( SKIP,   SKIP,  EXIST,   EXIST,  EXIST  ) ),
   ('Pascal',             '-cn', ( SKIP,   SKIP,  EXIST,   EXIST,  EXIST  ) ),
   ('Pascal2',            '-cn', ( SKIP,   SKIP,  EXIST,   EXIST,  EXIST  ) ),
   ('PimMod2',            '-cn', ( SKIP,   SKIP,  EXIST,   EXIST,  EXIST  ) ),
   #('Pretty',             '-cn', ( SKIP,   SKIP,  EXIST,   EXIST,  EXIST  ) ),
   ('Structs',            '-cn', ( SKIP,   SKIP,  EXIST,   EXIST,  EXIST  ) ),
   ('Umbriel1',           '-cn', ( SKIP,   SKIP,  ABSENT,  ABSENT, ABSENT ) ),
   ('Umbriel2',           '-cn', ( SKIP,   SKIP,  EXIST,   EXIST,  EXIST  ) ),
   ]


