'''
Created on 16.10.2015

@author: ruckt
'''

from __future__ import print_function

from pyparsing import Literal, operatorPrecedence, Word, opAssoc, nums,\
    ParserElement
ParserElement.enablePackrat()
from string import ascii_uppercase

def l(s):
    return Literal(s).suppress()

class Context(object):
        
    def __init__(self, base_ctx=None):
        self.atomics = set( base_ctx.atomics if base_ctx else () )
        self.valid_ctxs = base_ctx.valid_ctxs if base_ctx else []
        self.valid_ctxs.append(self)
    
    def add_variable(self, variable_name, flag):
        if (variable_name, not flag) in self.atomics:
            return False
        else:
            self.atomics.add((variable_name, flag))
            return True
        
    def __repr__(self):
        return repr(self.atomics)

class Element(object):
    
    order = None
    def prep(self, e):
        i = self.order.index(type(e))
        j = self.order.index(type(self))
        if i > j:
            return '(%r)' % e
        else:
            return repr(e)
        
    def keep(self, ctx, flag_left, flag_right):
        p1 = self.left.visit(ctx, flag_left)
        p2 = self.right.visit(ctx, flag_right)
        return p1 and p2
        
    def split(self, ctx, flag_left, flag_right):
        ctx.valid_ctxs.remove(ctx)
        ctx1 = Context(ctx)
        ctx2 = Context(ctx)
        p1 = self.left.visit(ctx1, flag_left)
        p2 = self.right.visit(ctx2, flag_right)
        if not p1:
            ctx.valid_ctxs.remove(ctx1)
        if not p2:
            ctx.valid_ctxs.remove(ctx2)
        return p1 or p2
    
    def equivalence(self, ctx, flags):
        ctx.valid_ctxs.remove(ctx)
        ctx1 = Context(ctx)
        ctx2 = Context(ctx)
        p1 = self.keep(ctx1, *flags[0:2])
        p2 = self.keep(ctx2, *flags[2:4])
        if not p1:
            ctx.valid_ctxs.remove(ctx1)
        if not p2:
            ctx.valid_ctxs.remove(ctx2)
        return p1 or p2
    
class Variable(Element):
    def __init__(self, toks):
        self.name = toks[0]
    def __repr__(self):
        return self.name
    def visit(self, ctx, flag):
        return ctx.add_variable(self.name, flag)
    
class Negation(Element):
    def __init__(self, toks):
        self.op = toks[0][1]
    def __repr__(self):
        return '~%s' % self.prep(self.op)
    def visit(self, ctx, flag):
        return self.op.visit(ctx, not flag)
    
class Conjunction(Element):
    def __init__(self, toks):
        self.left, _, self.right = toks[0]
    def __repr__(self):
        return '%s^%s' % (self.prep(self.left), self.prep(self.right))
    def visit(self, ctx, flag):
        if flag:
            return self.keep(ctx, True, True)
        else:
            return self.split(ctx, False, False)
    
class Disjunction(Element):
    def __init__(self, toks):
        self.left, _, self.right = toks[0]
    def __repr__(self):
        return '%sv%s' % (self.prep(self.left), self.prep(self.right))
    def visit(self, ctx, flag):
        if flag:
            return self.split(ctx, True, True)
        else:
            return self.keep(ctx, False, False)

class Implication(Element):
    def __init__(self, toks):
        self.left, _, self.right = toks[0]
    def __repr__(self):
        return '%s->%s' % (self.prep(self.left), self.prep(self.right))
    def visit(self, ctx, flag):
        if flag:
            return self.split(ctx, False, True)
        else:
            return self.keep(ctx, True, False)
    
class Equivalence(Element):
    def __init__(self, toks):
        self.left, _, self.right = toks[0]
    def __repr__(self):
        return '%s<->%s' % (self.prep(self.left), self.prep(self.right))
    def visit(self, ctx, flag,
              flag_combinations=[ (True, False, False, True),
                                  (True, True, False, False) ]):
        return self.equivalence(ctx, flag_combinations[flag])
    
Element.order=[Variable, Negation, Conjunction, Disjunction, Implication, Equivalence]
    
variable = Word(ascii_uppercase + nums).setParseAction(Variable)
operand = variable
expr = operatorPrecedence(operand, [
    (Literal('~'), 1, opAssoc.RIGHT, Negation),
    (Literal('^'), 2, opAssoc.LEFT, Conjunction),
    (Literal('v'), 2, opAssoc.LEFT, Disjunction),
    (Literal('->'), 2, opAssoc.LEFT, Implication),
    (Literal('<->'), 2, opAssoc.LEFT, Equivalence)
])

expr |= l('(') + expr + l(')') 

if __name__ == '__main__':
    tests = '''\
~A
A^B1
~(A^~A)
~(Av~B)
(AvB)^C
Av(BvC)
(A^B)vC
(A^B)^C
A^(B^C)
C^(AvB)
A^~A
B->~C
D<->E
A^(BvC->D)v(E<->A^C)
'''

    '''
'''
    for t in tests.splitlines():
        print(repr(t), end=': ')
        pred = expr.parseString(t, parseAll=True)[0]
        ctx = Context()
        print(end='' if pred.visit(ctx, True) else 'un')
        print('satisfiable')
        for c in ctx.valid_ctxs:
            print(end='{ ')
            print(end=', '.join( ('' if f else '~') + l for l,f in c.atomics))
            print(' }')
        