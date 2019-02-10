from myComplier import Complier


# <prog> → program <id>；<block>
# <block> → [<condecl>][<vardecl>][<proc>]<body>
# <condecl> → const <const>{,<const>}
# <const> → <id>:=<integer>
# <vardecl> → var <id>{,<id>}
# <proc> → procedure <id>（[<id>{,<id>}]）;<block>{;<proc>}
# <body> → begin <statement>{;<statement>}end
# <statement> → <id> := <exp>               
#                |if <lexp> then <statement>[else <statement>]
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
        ['vardecl1','body1'],
        ['condecl1','vardecl1','proc1','body1'],
        ['condecl1','proc1','body1'],
        ['proc1','body1'],
        ['vardecl1','proc1','body1'],
    ],
    'condecl1': [
        ['const','condecl2'],
    ],
    'condecl2': [
        ['const1',',','condecl2'],
        ['const1']
    ],
    'const1': [
        ['id',':=' ,'integer'],
    ],
    'vardecl1': [
        ['var','vardecl2'],
    ],
    'vardecl2':[
        ['id',',','vardecl2'],
        ['id']
    ],
    'proc1': [
        ['procedure','id','(','proc2',')','M3','proc3' ],
        ['procedure','id','(',')','M3','proc3' ]
    ],
    'M3':[
        [';']
    ],
    'proc2': [
        ['id'],
        ['id',',','proc2' ],
    ],
    'proc3': [
        ['block'],
        ['block',';','proc4'],
    ],
    'proc4':[
        ['proc1'],
        ['proc1','proc4'],
    ],
    'body1': [
        ['begin','body2'],
    ],
    'body2': [
        ['statement','end'],
        ['statement',';','body2'],
    ],
    #read和write都可以有多个参数
    'statement': [
        ['if','lexp','then','M1','statement'],
        ['if','lexp','then','M1','statement','N','else','M2','statement'],
        ['while','M1','lexp','do','M2','statement'],
        ['call','id','(','call1',')'],
        ['call','id','(',')'],
        ['id',':=','exp1'],
        ['read','(','id1',')'],
        ['write','(','exp',')'],
        ['body1']
    ],
    'id1':[
        ['id'],
        ['id',',','id1'],
    ],
    'exp':[
        ['exp1'],
        ['exp1',',','exp'],
    ],
    'call1':[
        ['exp1',',','call1'],
        ['exp1']
    ],
    'M1':[
        [':']
    ],
    'M2':[
        [':']
    ],
    'N':[
        [':']
    ],
    'lexp':[
        ['exp1', '<', 'exp1'],
        ['exp1', '>', 'exp1'],
        ['exp1', '<=', 'exp1'],
        ['exp1', '>=', 'exp1'],
        ['exp1', '==', 'exp1'],
        ['exp1', '!=', 'exp1'],
        ['exp1']
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
Complier.write_productions_to_file(start, productions)