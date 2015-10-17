'''
Created on 09.10.2015

@author: ruckt
'''

from __future__ import print_function

def resolve(cnf):
    
    for i, disjunction in enumerate(cnf):
        for flag, literal in disjunction:
            
            for j, disj_b in enumerate(cnf):
                if j != i and (not flag, literal) in disj_b:
                    new_clause = { (f,d) for f,d in disjunction | disj_b if d != literal }
                    
                    if not new_clause:
                        cnf.append(new_clause)
                        return False
                    
                    new_clause = { (f,d) for f,d in new_clause if not (not f, d) in new_clause }
                    
                    if not new_clause: # constructed a tautology..
                        continue                    
                    
                    if new_clause not in cnf:
                        cnf.append(new_clause)
                        return True

    return False
    
def print_clause(cnf):
    
    print('{ ', end='')
    for i, disjunction in enumerate(cnf):
        print('{', end='')
        for j, (flag, literal) in enumerate(disjunction):
            if not flag:
                print('~', end='')
            print(literal, end=', ' if j < len(disjunction) - 1 else '')
        print('}', end=', ' if i < len(cnf) - 1 else '')
    print(' }')

if __name__ == '__main__':
    
    cnf = [ { (True, 'A'), (False, 'B') }, { (False, 'A') }, { (True, 'B') } ]
    
    cnf = [ { (1, 'A'), (1, 'B'), (1, 'C') }, 
            { (0, 'A'), (0, 'B'), (0, 'C') },
            { (0, 'A'), (1, 'B'), (1, 'C') },
            { (1, 'B'), (0, 'C')},
            { (0, 'A'), (0, 'B'), (1, 'C') },
            #{ (1, 'A'), (1, 'C') },
            #{ (0, 'B'), (0, 'C')} ]
            ]
    
    print_clause(cnf)
    
    resume = True
    while resume:
        resume = resolve(cnf)
        print_clause(cnf)

    