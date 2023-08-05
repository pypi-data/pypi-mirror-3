import logging
logging.basicConfig(level=logging.INFO)

from integer.enum import enum

enum('Test', {'numeric_repr': hex},
     RED=1,
     GREEN=2,
     BLUE=3,
     CYAN=3,
     MAGENTA=1.1,
     YELLOW='4',
     )

def logval(val):
    logging.info('%s %r' % (val, val))

logval(RED)
logval(GREEN)
logval(BLUE)

for i in xrange(5):
    logval(Test(i))

def logcond(cond):
    logging.info('%s: %s' % (cond, eval(cond)))

logcond('RED == 1')
logcond('RED is 1')
logcond('RED == eval(repr(RED))')
logcond('RED is eval(repr(RED))')
logcond('RED == Test(1)')
logcond('RED is Test(1)')
logcond('RED == eval(repr(Test(1)))')
logcond('RED is eval(repr(Test(1)))')
