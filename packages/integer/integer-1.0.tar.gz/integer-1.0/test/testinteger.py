import logging
logging.basicConfig(level=logging.INFO)

from integer import Integer

class Test(Integer):
    def __str__(self):
        return 'Test(%d)' % self

a = Test(1)
b = Test(2)

def test_expr(expr):
    logging.info(' %s: %s' % (expr, eval(expr)))

test_expr('a + b')
test_expr('a + 1')
test_expr('1 + a')
test_expr('a + 1.0')

test_expr('-a')
test_expr('+a')
test_expr('abs(a)')
test_expr('abs(-a)')
test_expr('~a')

def test_statement(statement, expr):
    a = Test(1)
    b = Test(2)

    exec(statement)

    logging.info(' %s: %s' % (statement, eval(expr)))

test_statement('a += b', 'a')
test_statement('a += 1', 'a')

class Test2(Integer):
    def __str__(self):
        return 'Test2(%d)' % self

    def finalize_value(self, val, fname, *args):
        if len(args) == 1 and isinstance(args[0], Test):
            return Test(val)
        return Integer.finalize_value(self, val, fname, *args)

c = Test2(3)

test_expr('a + c')
test_expr('c + a')

def test_statement(statement, expr):
    a = Test(1)
    b = Test2(2)

    exec(statement)

    logging.info(' %s: %s' % (statement, eval(expr)))

test_statement('a += b', 'a')
test_statement('b += a', 'b')
