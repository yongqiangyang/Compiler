from CompilerFront import compiler

# P -> { } | { AA }
# AA-> A | A AA
# A -> DD | SS
# DD-> D DD | D
# D -> T ID FH
# ID-> id | id = id | id = num | ID , ID
# T -> T [ num ] | TY
# TY->int | float | char | bool
# SS-> S | S SS
# S -> L = E FH | if ( B ) S | if ( B ) S else S | while ( B ) S | do S while ( B ) FH | break FH | continue FH | P
# B -> B or B | B and B | ! B | ( B ) | E < E | E > E | E <= E | E >= E | E == E | E != E | true | false
# E -> E + E | E - E | E * E | E / E | L | ( E ) | num | id
# L -> id [ E ] | id
# FH-> ; | FH ;


#这是什么数据类型？字典？
productions = {
    'P': [
        ['{', 'AA', '}'],
        ['{', '}'],
    ],
    'AA': [
        ['A', ],
        ['A', 'AA']
    ],
    'A': [
        ['DD', ],
        ['SS', ]
    ],
    'DD': [
        ['D', 'DD'],
        ['D', ],
    ],
    'D': [
        ['T', 'ID', 'FH'],
    ],
    'ID': [
        ['id', ],
        ['id', '=', 'id'],
        ['id', '=', 'num'],
        ['ID', ',', 'ID'],
    ],
    'T': [
        ['T', '[', 'num', ']'],
        ['TY', ],
    ],
    'TY': [
        ['int', ],
        ['float', ],
        ['char', ],
        ['bool', ],
        ['double', ],
    ],
    'SS': [
        ['S', 'SS'],
        ['S', ],
    ],
    'S': [
        ['L', '=', 'E', 'FH'],
        ['if', '(', 'B', ')', 'S'],
        ['if', '(', 'B', ')', 'S', 'else', 'S'],
        ['while', '(', 'B', ')', 'S'],
        ['while', '(', 'B', ')', 'FH'],
        ['do', 'S', 'while', '(', 'B', ')', 'FH'],
        ['break', 'FH'],
        ['continue', 'FH'],
        ['P', ],
    ],
    'B': [
        ['B', 'or', 'B'],
        ['B', 'and', 'B'],
        ['!', 'B'],
        ['(', 'B', ')'],
        ['E', '<', 'E'],
        ['E', '>', 'E'],
        ['E', '<=', 'E'],
        ['E', '>=', 'E'],
        ['E', '==', 'E'],
        ['E', '!=', 'E'],
        ['true', ],
        ['false', ],
    ],
    'E': [
        ['E', '+', 'E'],
        ['E', '-', 'E'],
        ['E', '*', 'E'],
        ['E', '/', 'E'],
        ['L', ],
        ['(', 'B', ')'],
        ['num', ],
        ['id', ],
    ],
    'L': [
        ['L', '[', 'E', ']', ],
        ['id', ],
    ],
    'FH': [
        [';', ],
        [';', 'FH', ],
    ]
}
start = 'P'
compiler.write_productions_to_file(start, productions)