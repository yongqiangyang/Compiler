from myComplier import myCompiler

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

# <prog> → program <id>；<block>
# <block> → [<condecl>][<vardecl>][<proc>]<body>
# <condecl> → const <const>{,<const>}
# <const> → <id>:=<integer>
# <vardecl> → var <id>{,<id>}
# <proc> → procedure <id>（[<id>{,<id>}]）;<block>{;<proc>}
# <body> → begin <statement>{;<statement>}end
# <statement> → <id> := <exp>               
# |if <lexp> then <statement>[else <statement>]
#                |while <lexp> do <statement>
#                |call <id>[（<exp>{,<exp>}）]
#                |<body>
#                |read (<id>{，<id>})
#                |write (<exp>{,<exp>})
# <lexp> → <exp> <lop> <exp>|odd <exp>
# <exp> → [+|-]<term>{<aop><term>}
# <term> → <factor>{<mop><factor>}
# <factor>→<id>|<integer>|(<exp>)
# <lop> → =|<>|<|<=|>|>=
# <aop> → +|-
# <mop> → *|/
# <id> → l{l|d}   （注：l表示字母）
# <integer> → d{d}


#这是什么数据类型？
productions = {
    'prog': [
        ['program','id',';','block'],
    ],
    'block': [
        ['body1'],
        ['condecl1','body1' ],
        ['condecl1','vardecl1','body1'],
        ['condecl1','vardecl1','proc1','body1'],
    ],
    'condecl1': [
        ['const','condecl2'],
    ],
    'condecl2': [
        ['const1',',','condecl2'],
        ['condecl3']
    ],
    'condecl3': [
        ['const1',';'],
    ],
    'const1': [
        ['id',':=' ,'integer'],
    ],
    'vardecl1': [
        ['var','vardecl2'],
    ],
    'vardecl2': [
        ['id','vardecl3'],
        ['id',',','vardecl2'],
    ],
    'vardecl3': [
        [';'],
    ],
    'proc1': [
        ['procedure','id','(','proc2',')','proc3' ],
    ],
    'proc2': [
        ['id'],
        ['id',',','proc2' ],
    ],
    'proc3': [
        ['block'],
        ['block',';','proc1'],
    ],
    'body1': [
        ['begin','body2'],
    ],
    'body2': [
        ['body3'],
        ['statement',';','body2'],
    ],
    'body3': [
        ['end'],
    ],
    'statement': [
        ['id',':=','exp1'],
        ['if','lexp','then','statement'],
        ['if','lexp','then','statement','else','statement'],
        ['while','lexp','do','statement'],
        ['call','id'],
        ['read','id'],
        ['write','exp1']
    ],
    'lexp':[
        ['exp1', '<', 'exp1'],
        ['exp1', '>', 'exp1'],
        ['exp1', '<=', 'exp1'],
        ['exp1', '>=', 'exp1'],
        ['exp1', '==', 'exp1'],
        ['exp1', '!=', 'exp1'],
    ],
    'exp1': [
        ['exp1', '+', 'exp2'],
        ['exp1', '-', 'exp2'],
        ['exp2']
    ],
    'exp2':[
        ['exp2','*','exp3'],
        ['exp2','/','exp3'],
        ['exp3']
    ],
    'exp3':[
        ['(','exp1',')'],
        ['integer', ],
        ['id', ],
    ]
}
start = 'prog'
myCompiler.write_productions_to_file(start, productions)