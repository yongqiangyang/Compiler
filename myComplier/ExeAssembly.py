from pprint import pprint
import os, sys
import copy
import random
from myComplier import Complier
from myComplier import fourToAss


class ExeAssembly:
    """
    输入一个文件路径,执行汇编指令
    """
    def __init__(self, filename):
        #####################################################
        #CODE   用来存放程序代码                             #
        #STACK  （栈）用来动态分配数据空间                    #
        #EIX    存放当前要执行的指令                         #
        #ETX    指向数据栈stack的栈顶                        #
        #EBX    存放当前运行过程的数据区在stack中的起始位置   #
        #EPX    存放下一条要执行的指令                       #
        #####################################################
        self.file_name = filename   #存文件名
        self.assemblyEle=list()     #目标代码：汇编代码
        self.variable = list()      #变量
        self.constant = list()      #常量
        self.intermediate = list()  #中间变量（temp）
        self.level = 0              #层次差
        self.funcname = []           #函数名
        self.jmp_nam = dict()       #跳转名dict[location:name]
        self.outputSTACK = []       #用于输出
        self.STACK = []             #数据栈
        self.writeResult = []       #执行输出结果
        self.flagRegister =''       #标志寄存器
        self.EIX =int(0)            #存放当前要执行的指令
        self.EPX =int(0)            #存放下一条要执行的指令
        self.EBX =int(0)            #存放当前运行过程的数据区在stack中的起始位置
        self.ETX =int(0)            #指向数据栈stack的栈顶

        #读取汇编代码
        string_assembly=open(filename+'_midcode.txt','r').read()
        raw_string_assembly=string_assembly.split('\n')
        for element in raw_string_assembly:
            List = element.split()
            self.assemblyEle.append(List)

        #读入变量
        string_two = open(filename + '.two', 'r').read()
        raw_string_two = string_two.split('\n')
        status=''
        for element in raw_string_two:
            List = element.split()
            if status=='const' and List[1]=='id':
                self.constant.append(List[0])
            elif status=='var' and List[1]=='id':
                self.variable.append(List[0])
            elif status == 'procedure' and List[1] == 'id':
                self.funcname.append(List[0])
            else:
                pass
            if List[1]=='const':
                status='const'
            elif List[1]=='var':
                status='var'
            elif List[1]=='begin':
                status=''
            elif List[1]=='procedure':
                status='procedure'
        set_ = set(self.constant)
        self.constant = list(set_)


        #pprint(self.assemblyEle)
        ##删除中间文件
        #os.remove(filename + '.four')
        #os.remove(filename + '.two')

    ##处理运算符
    def add(self):
        '''加法操作'''
        result = self.STACK[-1] + self.STACK[-2]
        self.STACK.pop()
        self.STACK.pop()
        self.STACK.append(result)
        tempstack = copy.deepcopy(self.STACK)
        self.outputSTACK.append(tempstack)
        return True

    def neg(self):
        '''取反操作'''
        pass

    def sub(self):
        '''减法操作'''
        result = self.STACK[-2] - self.STACK[-1]
        self.STACK.pop()
        self.STACK.pop()
        self.STACK.append(result)
        tempstack = copy.deepcopy(self.STACK)
        self.outputSTACK.append(tempstack)
        return True

    def mul(self):
        '''乘法操作'''
        result = self.STACK[-2] * self.STACK[-1]
        self.STACK.pop()
        self.STACK.pop()
        self.STACK.append(result)
        tempstack = copy.deepcopy(self.STACK)
        self.outputSTACK.append(tempstack)
        return True

    def div(self):
        '''除法操作'''
        result = self.STACK[-2] + self.STACK[-1]
        self.STACK.pop()
        self.STACK.pop()
        self.STACK.append(result)
        tempstack = copy.deepcopy(self.STACK)
        self.outputSTACK.append(tempstack)
        return True

    def equal(self):
        '''恒等条件操作'''
        result = self.STACK[-2] == self.STACK[-1]
        self.STACK.pop()
        self.STACK.pop()
        if result:
            self.flagRegister = 'true'
        else:
            self.flagRegister = 'false'
        return True

    def unequal(self):
        '''不等条件操作'''
        result = self.STACK[-2] != self.STACK[-1]
        self.STACK.pop()
        self.STACK.pop()
        if result:
            self.flagRegister = 'true'
        else:
            self.flagRegister = 'false'
        return True

    def below(self):
        '''小于的条件操作'''
        result = self.STACK[-2] < self.STACK[-1]
        self.STACK.pop()
        self.STACK.pop()
        if result:
            self.flagRegister = 'true'
        else:
            self.flagRegister = 'false'
        return True

    def below_equal(self):
        '''小于等于的条件操作'''
        result = self.STACK[-2] <= self.STACK[-1]
        self.STACK.pop()
        self.STACK.pop()
        if result:
            self.flagRegister='true'
        else:
            self.flagRegister='false'
        return True

    def above(self):
        '''大于的条件操作'''
        result = self.STACK[-2] > self.STACK[-1]
        self.STACK.pop()
        self.STACK.pop()
        if result:
            self.flagRegister = 'true'
        else:
            self.flagRegister = 'false'
        return True

    def above_equal(self):
        '''大于等于的条件操作'''
        result = self.STACK[-2] >= self.STACK[-1]
        self.STACK.pop()
        self.STACK.pop()
        if result:
            self.flagRegister = 'true'
        else:
            self.flagRegister = 'false'
        return True

    def negation(self):
        '''非的条件操作'''
        pass

    switch_operation = {#以后再进行编号
        '+': add,
        '-': sub,
        '*': mul,
        '/': div,
        '==': equal,
        '!=': unequal,
        '<': below,
        '<=': below_equal,
        '>': above,
        '>=': above_equal,
        '!': negation,
    }

    ##处理操作
    def operation(self):
        '''处理运算符'''
        if not self.switch_operation[self.operator](self):
            print('error index %s: unkown character "%s", 003' % (str([self.operator,self.source1,self.source2,self.dest]), self.dest), end='\n\n')
            return False
        return True

    #给常量赋值
    def mov(self):
        if self.source1[0]=='[':
            source1=self.source1[1:-1]
            ind=int(source1)
            self.STACK[ind] = int(self.source2)
            tempstack = copy.deepcopy(self.STACK)
            self.outputSTACK.append(tempstack)
        elif self.source1=='EBX' and self.source2=='0':
            self.EBX=0
        elif self.source1=='ETX' and self.source2=='EBX':
            self.ETX=self.EBX
        elif self.source1=='EBX' and self.source2=='ETX':
            self.EBX=self.ETX
        else:
            return False
        return True

    #取常量a放入数据栈栈顶
    def lit(self):
        ind=int(self.source2)
        self.STACK.append(self.STACK[ind])
        tempstack = copy.deepcopy(self.STACK)
        self.outputSTACK.append(tempstack)
        return True

    switch_opr = {  # 以后再进行编号
        '+': add,
        '-': sub,
        '*': mul,
        '/': div,
        '==': equal,
        '!=': unequal,
        '<': below,
        '<=': below_equal,
        '>': above,
        '>=': above_equal,
        '!': negation,
    }

    def opr(self):
        if not self.switch_opr[self.source2](self):
            print('error index %s: unkown character "%s", OPR' % (str([self.operator,self.source1,self.source2]), self.source2), end='\n\n')
            return False
        return True

    def sto(self):
        ind=int(self.source2)
        self.STACK[ind]=self.STACK[-1]
        tempstack = copy.deepcopy(self.STACK)
        self.outputSTACK.append(tempstack)
        return True

    def lod(self):
        ind=int(self.source2)
        self.STACK.append(self.STACK[ind])
        tempstack = copy.deepcopy(self.STACK)
        self.outputSTACK.append(tempstack)
        return True

    def wrt(self):
        self.writeResult.append(self.STACK[-1])
        return True

    def red(self):
        num=input("read:")
        ind=int(self.source2)
        self.STACK[ind]=num
        tempstack = copy.deepcopy(self.STACK)
        self.outputSTACK.append(tempstack)
        return True

    def jpc(self):
        if self.flagRegister == 'true':
            ind=int(self.source2)
            self.EPX= ind
        return True

    def jmp(self):
        ind = int(self.source2)
        self.EPX = ind
        return True

    def push(self):
        if self.source1.isdigit():
            ind =int(self.source1)
            self.STACK.append(ind)
            tempstack = copy.deepcopy(self.STACK)
            self.outputSTACK.append(tempstack)
            return True
        elif self.source1=='ETX':
            self.ETX=len(self.STACK)
            self.STACK.append(self.ETX)
            tempstack = copy.deepcopy(self.STACK)
            self.outputSTACK.append(tempstack)
            return True
        elif self.source1=='EBX':
            self.STACK.append(self.EBX)
            tempstack = copy.deepcopy(self.STACK)
            self.outputSTACK.append(tempstack)
            return True
        elif self.source1=='EPX':
            self.STACK.append(self.EPX)
            tempstack = copy.deepcopy(self.STACK)
            self.outputSTACK.append(tempstack)
            return True
        elif self.source1=='EIX':
            self.STACK.append(self.EIX)
            tempstack = copy.deepcopy(self.STACK)
            self.outputSTACK.append(tempstack)
            return True

    def pop(self):
        return True

    def inc(self):
        for i in range(int(self.source2)):
            self.STACK.append(0)
        tempstack = copy.deepcopy(self.STACK)
        self.outputSTACK.append(tempstack)
        return True

    #处理调用指令
    def call(self):
        #压入下一条指令地址
        self.STACK.append(self.EPX)
        #压入基地址
        self.STACK.append(self.EBX)
        self.ETX=len(self.STACK)
        #让基地址指向栈顶
        self.EBX=self.ETX
        ind=int(self.source2)
        #跳转到子程序
        self.EPX=ind
        return True

    def ret(self):
        #将子程序内容出栈
        self.ETX=len(self.STACK)
        for i in range(self.ETX-self.EBX):
            self.STACK.pop()
        #退出基地址
        self.EBX=self.STACK.pop()
        #退出当前执行指令地址
        self.EIX=self.EPX=self.STACK.pop()
        return True

    def nop(self):
        return True
    def end(self):
        self.EIX=len(self.assemblyEle)-1
        return True

    switch_ = {
        'MOV': mov,
        'LIT': lit,
        'OPR': opr,
        'STO': sto,
        'LOD': lod,
        'WRT': wrt,
        'JPC': jpc,
        'JMP': jmp,
        'RED': red,
        'PUSH':push,
        'INC': inc,
        'POP': pop,
        'CALL':call,
        'RET': ret,
        'NOP': nop,
        'END':end,
        ##################################
        #'pushc': pushconstant,  #LIT 0, a
        #'pushv': pushvariable,  #LOD L, a
        #'pop': pop,             #STO L, a
        #'call': call,           #CALL L, a<<<---TUDO
        #'inc': inc,             #INT 0, a
        # 'jmp': jmp,             #JMP 0, a
        # 'jcc': jcc,             #JPC 0, a
        # 'read': read,           #RED L, a
        # 'write': write,         #WRT 0, 0
        #############操作立即数############
        #                        #MOV [a], i
        #                        #PUSH i
        #############操作寄存器############
        #                        #MOV R, R/a
        #                        #PUSH R
        #                        #POP R
        ###################################
    }

    def transform(self):
        '''由本函数进行执行汇编指令操作，并输出数据栈变化过程以及输出结果  '''

        #处理汇编代码
        self.operator = ''
        self.source1 = ''
        self.source2 = ''
        while self.EIX != len(self.assemblyEle)-1:
            self.EIX=self.EPX
            self.EPX=self.EPX+1
            self.element=self.assemblyEle[self.EIX]
            self.operator = self.element[0]
            if self.element[0] not in ['PUSH','RET','NOP','END']:
                self.source1 = self.element[1][:-1]
                self.source2 = self.element[2]
            elif self.element[0] == 'PUSH':
                self.source1 =self.element[1]

            if self.element[0] == 'MOV':
                case = 'MOV'
            elif self.element[0] == 'LIT':
                case = 'LIT'
            elif self.element[0] == 'OPR':
                case = 'OPR'
            elif self.element[0] == 'STO':
                case = 'STO'
            elif self.element[0] == 'LOD':
                case = 'LOD'
            elif self.element[0] in 'WRT':
                case = 'WRT'
            elif self.element[0] in 'JPC':
                case = 'JPC'
            elif self.element[0] in 'JMP':
                case = 'JMP'
            elif self.element[0] in 'RED':
                case = 'RED'
            elif self.element[0] in 'PUSH':
                case = 'PUSH'
            elif self.element[0] in 'INC':
                case = 'INC'
            elif self.element[0] in 'POP':
                case = 'POP'
            elif self.element[0] in 'CALL':
                case = 'CALL'
            elif self.element[0] in 'RET':
                case = 'RET'
            elif self.element[0] in 'NOP':
                case = 'NOP'
            elif self.element[0] in 'END':
                case = 'END'
            # 不合法字符，报错退出循环
            else:
                print('error index %s: unkown character "%s", 001' % (str(self.element), self.element[0]), end='\n\n')
                return False
            if not self.switch_[case](self):
                print('error index %s: unkown character "%s", 002' % (str(self.element), self.element[0]), end='\n\n')
                return False

        #pprint(self.code_str)
        #输出目标机代码

        print("输出结果: ")
        pprint(self.writeResult)
        with open(self.file_name + '_writeResult'+'.txt', 'w') as f:
            f.write(str(self.writeResult))
        print("数据栈过程: ")
        pprint(self.outputSTACK)
        with open(self.file_name + '_outputSTACK'+'.txt', 'w') as f:
            f.write(str(self.outputSTACK))

if __name__ == '__main__':
    file_name='test5'
    analyzer = Complier.Compiler()
    # analyzer.analyse("input.txt")
    # analyzer.analyse("input_if.txt")
    # analyzer.analyse("input_while_do.txt")
    # analyzer.analyse("input_if&&while.txt")
    # analyzer.analyse("input_call_write_read.txt")
    # analyzer.analyse("input_finaly.txt")
    # analyzer.analyse("input_proc.txt")
    # analyzer.analyse("if_test.txt")
    analyzer.analyse(file_name+'.txt')
    m2d = fourToAss.Mcode2destination(file_name)
    m2d.transform()
    ExeAss = ExeAssembly(file_name)
    ExeAss.transform()