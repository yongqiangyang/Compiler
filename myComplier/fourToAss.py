from pprint import pprint
import os, sys
import random
import re

class Mcode2destination:
    """
    输入一个文件路径,进行四元式转化为目标机代码
    主要函数：
        .transform()    开始进行进行四元式到目标机代码的转化，将结果输出到"|filename|_output.txt"的文件中
    """
    def __init__(self, filename):
        #####################################################
        #CODE   用来存放程序代码                            #
        #STACK  （栈）用来动态分配数据空间                  #
        #EIX    存放当前要执行的指令                        #
        #ETX    指向数据栈stack的栈顶                       #
        #EBX    存放当前运行过程的数据区在stack中的起始位置 #
        #EPX    存放下一条要执行的指令                      #
        ##################################################### 
        self.file_name = filename   #存文件名
        self.fourEle = list()       #四元式
        self.variable = list()      #变量
        self.constant = list()      #常量
        self.intermediate = list()  #中间变量（temp）
        self.level = 0              #层次差
        self.funcname = list()      #函数名
        self.jmp_nam = dict()       #跳转名dict[location:name]
        self.level_fourEle = dict() #存放call的四元式代码

        #读入四元式(并记录jmp的地址)
        string_four = open(filename + '.four', 'r').read()
        raw_string_four = string_four.split('\n')
        for element in raw_string_four:
            List = element.split()
            self.fourEle.append(List)
            if 'j' in List[1]:
                self.jmp_nam[str(List[4])] = self.jmp_name()

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

        ##删除中间文件
        #os.remove(filename + '.four')
        #os.remove(filename + '.two')

    #判断是不是变量
    def is_variable(self, string):
        '''判断是不是变量'''
        if string in self.variable:
            return True
        else:
            return False

    #判断是不是中间变量
    def is_intermediate(self, string):
        '''判断是不是中间变量'''
        if string in self.intermediate:
            return True
        else:
            return False
    #判断是不是常量
    def is_constant(self, string):
        '''判断是不是常量'''
        if string in self.constant:
            return True
        else:
            return False

    ##处理运算符    
    def add(self):
        '''加法操作'''
        if self.source2 == '_':
            print('error index %s: misusage about "%s", 004' % (str([self.operator,self.source1,self.source2,self.dest]), self.dest), end='\n\n')
            return False
        else:
            code = ''
            if self.is_variable(self.source1):
                ind = len(self.constant) + self.variable.index(self.source1) 
                code += 'LOD %d, %d{%s}\n' % (self.level, ind, self.source1)
            elif self.is_intermediate(self.source1):
                ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.source1)
                del self.intermediate[self.intermediate.index(self.source1)]
                code += 'LIT 0, %d{%s}\n' % (ind, self.source1)
            elif self.is_constant(self.source1):
                ind = self.constant.index(self.source1) 
                code += 'LIT 0, %d{%s}\n' % (ind, self.source1)
            elif self.source1.isnumeric():
                code += 'PUSH %d{Immediate}\n' % int(self.source1)
            if self.is_variable(self.source2):
                ind = len(self.constant) + self.variable.index(self.source2) 
                code += 'LOD %d, %d{%s}\n' % (self.level, ind, self.source2)
            elif self.is_constant(self.source2):
                ind = self.constant.index(self.source2) 
                code += 'LIT 0, %d{%s}\n' % (ind, self.source2)
            elif self.is_intermediate(self.source2):
                ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.source2)
                del self.intermediate[self.intermediate.index(self.source2)]
                code += 'LIT 0, %d{%s}\n' % (ind, self.source2)
            elif self.source2.isnumeric():
                 code += 'PUSH %d{Immediate}\n' % int(self.source2)
            code += 'OPR 0, +\n'
            if self.dest in self.variable:
                ind = len(self.constant) + self.variable.index(self.source1)
                code += 'STO %d, %d{%s}\n' % (self.level, ind, self.dest)
            elif 'temp' in self.dest:
                if len(self.intermediate) > 2:
                    print('error length intermediate')
                self.intermediate.append(self.dest)
                ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.dest)
                code += 'STO %d, %d{%s}\n' % (self.level, ind, self.dest) 
            self.code.append(code)
            return True
        return False

    def neg(self):
        '''取反操作'''
        pass

    def sub(self):
        '''减法操作'''
        if self.source2 == '_':
            self.neg()
            pass
        else:
            code = ''
            if self.is_variable(self.source1):
                ind = len(self.constant) + self.variable.index(self.source1) 
                code += 'LOD %d, %d{%s}\n' % (self.level, ind, self.source1)
            elif self.is_intermediate(self.source1):
                ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.source1)
                del self.intermediate[self.intermediate.index(self.source1)]
                code += 'LIT 0, %d{%s}\n' % (ind, self.source1)
            elif self.is_constant(self.source1):
                ind = self.constant.index(self.source1) 
                code += 'LIT 0, %d{%s}\n' % (ind, self.source1)
            elif self.source1.isnumeric():
                code += 'PUSH %d{Immediate}\n' % int(self.source1)
            if self.is_variable(self.source2):
                ind = len(self.constant) + self.variable.index(self.source2) 
                code += 'LOD %d, %d{%s}\n' % (self.level, ind, self.source2)
            elif self.is_constant(self.source2):
                ind = self.constant.index(self.source2) 
                code += 'LIT 0, %d{%s}\n' % (ind, self.source2)
            elif self.is_intermediate(self.source2):
                ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.source2)
                del self.intermediate[self.intermediate.index(self.source2)]
                code += 'LIT 0, %d{%s}\n' % (ind, self.source2)
            elif self.source2.isnumeric():
                 code += 'PUSH %d{Immediate}\n' % int(self.source2)
            code += 'OPR 0, -\n'
            if self.dest in self.variable:
                ind = len(self.constant) + self.variable.index(self.source1)
                code += 'STO %d, %d{%s}\n' % (self.level, ind, self.dest)
            elif 'temp' in self.dest:
                if len(self.intermediate) > 2:
                    print('error length intermediate')
                self.intermediate.append(self.dest)
                ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.dest)
                code += 'STO %d, %d{%s}\n' % (self.level, ind, self.dest) 
            self.code.append(code)
            return True
        pass

    def mul(self):
        '''乘法操作'''
        code = ''
        if self.is_variable(self.source1):
            ind = len(self.constant) + self.variable.index(self.source1) 
            code += 'LOD %d, %d{%s}\n' % (self.level, ind, self.source1)
        elif self.is_intermediate(self.source1):
            ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.source1)
            del self.intermediate[self.intermediate.index(self.source1)]
            code += 'LIT 0, %d{%s}\n' % (ind, self.source1)
        elif self.is_constant(self.source1):
            ind = self.constant.index(self.source1) 
            code += 'LIT 0, %d{%s}\n' % (ind, self.source1)
        elif self.source1.isnumeric():
            code += 'PUSH %d{Immediate}\n' % int(self.source1)
        if self.is_variable(self.source2):
            ind = len(self.constant) + self.variable.index(self.source2) 
            code += 'LOD %d, %d{%s}\n' % (self.level, ind, self.source2)
        elif self.is_constant(self.source2):
            ind = self.constant.index(self.source2) 
            code += 'LIT 0, %d{%s}\n' % (ind, self.source2)
        elif self.is_intermediate(self.source2):
            ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.source2)
            del self.intermediate[self.intermediate.index(self.source2)]
            code += 'LIT 0, %d{%s}\n' % (ind, self.source2)
        elif self.source2.isnumeric():
             code += 'PUSH %d{Immediate}\n' % int(self.source2)
        code += 'OPR 0, *\n'
        if self.dest in self.variable:
            ind = len(self.constant) + self.variable.index(self.source1)
            code += 'STO %d, %d{%s}\n' % (self.level, ind, self.dest)
        elif 'temp' in self.dest:
            if len(self.intermediate) > 2:
                print('error length intermediate')
            self.intermediate.append(self.dest)
            ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.dest)
            code += 'STO %d, %d{%s}\n' % (self.level, ind, self.dest) 
        self.code.append(code)
        return True

    def div(self):
        '''除法操作'''
        code = ''
        if self.is_variable(self.source1):
            ind = len(self.constant) + self.variable.index(self.source1) 
            code += 'LOD %d, %d{%s}\n' % (self.level, ind, self.source1)
        elif self.is_intermediate(self.source1):
            ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.source1)
            del self.intermediate[self.intermediate.index(self.source1)]
            code += 'LIT 0, %d{%s}\n' % (ind, self.source1)
        elif self.is_constant(self.source1):
            ind = self.constant.index(self.source1) 
            code += 'LIT 0, %d{%s}\n' % (ind, self.source1)
        elif self.source1.isnumeric():
            code += 'PUSH %d{Immediate}\n' % int(self.source1)
        if self.is_variable(self.source2):
            ind = len(self.constant) + self.variable.index(self.source2) 
            code += 'LOD %d, %d{%s}\n' % (self.level, ind, self.source2)
        elif self.is_constant(self.source2):
            ind = self.constant.index(self.source2) 
            code += 'LIT 0, %d{%s}\n' % (ind, self.source2)
        elif self.is_intermediate(self.source2):
            ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.source2)
            del self.intermediate[self.intermediate.index(self.source2)]
            code += 'LIT 0, %d{%s}\n' % (ind, self.source2)
        elif self.source2.isnumeric():
            if not int(self.source2):
                print('error :Divide Fault')
                return False
            code += 'PUSH %d{Immediate}\n' % int(self.source2)
        code += 'OPR 0, *\n'
        if self.dest in self.variable:
            ind = len(self.constant) + self.variable.index(self.source1)
            code += 'STO %d, %d{%s}\n' % (self.level, ind, self.dest)
        elif 'temp' in self.dest:
            if len(self.intermediate) > 2:
                print('error length intermediate')
            self.intermediate.append(self.dest)
            ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.dest)
            code += 'STO %d, %d{%s}\n' % (self.level, ind, self.dest) 
        self.code.append(code)
        return True

    def evaluation(self):
        '''赋值操作'''
        code = ''
        if self.dest.isnumeric() or self.is_intermediate(self.dest):
            print('error index %s: bad operator "%s"' % (str([self.operator,self.source1,self.source2,self.dest]), self.dest), end='\n\n')
            return False
        elif self.is_intermediate(self.source1):
            ind_d = self.intermediate.index(self.source1)
            ind = len(self.constant) + len(self.variable) + ind_d
            del self.intermediate[ind_d]
            code = 'LOD %d, %d{%s}\n' % (self.level, ind, self.source1)
        elif self.is_variable(self.source1):
            ind = len(self.constant) + self.variable.index(self.source1)
            code = 'LOD %d, %d{%s}\n' % (self.level, ind, self.source1)
        elif self.is_constant(self.source1):
            ind = self.constant.index(self.source1)
            code = 'LIT 0, %d{%s}\n' % (ind, self.source1)
        elif self.source1.isnumeric():
            if self.dest in self.variable:
                code = 'PUSH %d{Immediate}\n' % (int(self.source1))
            elif self.dest in self.constant:
                ind = self.constant.index(self.dest)
                code = 'MOV [%d]{%s}, %d{Immediate}\n' % (ind, self.dest, int(self.source1))
                self.code.append(code)
                return True
        else :
            print('error 404')
            return False
        if self.dest in self.variable:
                ind = len(self.constant) + self.variable.index(self.dest)
                code += 'STO %d, %d{%s}\n' % (self.level, ind, self.dest)
        elif self.dest in self.constant:
                ind = self.constant.index(self.dest)
                code += 'STO %d, %d{%s}\n' % (0, ind, self.dest)
        self.code.append(code)
        return True 

    def equal(self):
        '''恒等条件操作'''
        code = ''
        if self.is_variable(self.source1):
            ind = len(self.constant) + self.variable.index(self.source1) 
            code += 'LOD %d, %d{%s}\n' % (self.level, ind, self.source1)
        elif self.is_intermediate(self.source1):
            ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.source1)
            del self.intermediate[self.intermediate.index(self.source1)]
            code += 'LIT 0, %d{%s}\n' % (ind, self.source1)
        elif self.is_constant(self.source1):
            ind = self.constant.index(self.source1) 
            code += 'LIT 0, %d{%s}\n' % (ind, self.source1)
        elif self.source1.isnumeric():
            code += 'PUSH %d{Immediate}\n' % int(self.source1)
        if self.is_variable(self.source2):
            ind = len(self.constant) + self.variable.index(self.source2) 
            code += 'LOD %d, %d{%s}\n' % (self.level, ind, self.source2)
        elif self.is_constant(self.source2):
            ind = self.constant.index(self.source2) 
            code += 'LIT 0, %d{%s}\n' % (ind, self.source2)
        elif self.is_intermediate(self.source2):
            ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.source2)
            del self.intermediate[self.intermediate.index(self.source2)]
            code += 'LIT 0, %d{%s}\n' % (ind, self.source2)
        elif self.source2.isnumeric():
             code += 'PUSH %d{Immediate}\n' % int(self.source2)
        code += 'OPR 0, ==\n'
        if self.dest in self.variable:
            ind = len(self.constant) + self.variable.index(self.source1)
            code += 'STO %d, %d{%s}\n' % (self.level, ind, self.dest)
        elif 'temp' in self.dest:
            if len(self.intermediate) > 2:
                print('error length intermediate')
            self.intermediate.append(self.dest)
            ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.dest)
            code += 'STO %d, %d{%s}\n' % (self.level, ind, self.dest) 
        self.code.append(code)
        return True

    def unequal(self):
        '''不等条件操作'''
        code = ''
        if self.is_variable(self.source1):
            ind = len(self.constant) + self.variable.index(self.source1) 
            code += 'LOD %d, %d{%s}\n' % (self.level, ind, self.source1)
        elif self.is_intermediate(self.source1):
            ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.source1)
            del self.intermediate[self.intermediate.index(self.source1)]
            code += 'LIT 0, %d{%s}\n' % (ind, self.source1)
        elif self.is_constant(self.source1):
            ind = self.constant.index(self.source1) 
            code += 'LIT 0, %d{%s}\n' % (ind, self.source1)
        elif self.source1.isnumeric():
            code += 'PUSH %d{Immediate}\n' % int(self.source1)
        if self.is_variable(self.source2):
            ind = len(self.constant) + self.variable.index(self.source2) 
            code += 'LOD %d, %d{%s}\n' % (self.level, ind, self.source2)
        elif self.is_constant(self.source2):
            ind = self.constant.index(self.source2) 
            code += 'LIT 0, %d{%s}\n' % (ind, self.source2)
        elif self.is_intermediate(self.source2):
            ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.source2)
            del self.intermediate[self.intermediate.index(self.source2)]
            code += 'LIT 0, %d{%s}\n' % (ind, self.source2)
        elif self.source2.isnumeric():
             code += 'PUSH %d{Immediate}\n' % int(self.source2)
        code += 'OPR 0, !=\n'
        if self.dest in self.variable:
            ind = len(self.constant) + self.variable.index(self.source1)
            code += 'STO %d, %d{%s}\n' % (self.level, ind, self.dest)
        elif 'temp' in self.dest:
            if len(self.intermediate) > 2:
                print('error length intermediate')
            self.intermediate.append(self.dest)
            ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.dest)
            code += 'STO %d, %d{%s}\n' % (self.level, ind, self.dest) 
        self.code.append(code)
        return True

    def below(self):
        '''小于的条件操作'''
        code = ''
        if self.is_variable(self.source1):
            ind = len(self.constant) + self.variable.index(self.source1) 
            code += 'LOD %d, %d{%s}\n' % (self.level, ind, self.source1)
        elif self.is_intermediate(self.source1):
            ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.source1)
            del self.intermediate[self.intermediate.index(self.source1)]
            code += 'LIT 0, %d{%s}\n' % (ind, self.source1)
        elif self.is_constant(self.source1):
            ind = self.constant.index(self.source1) 
            code += 'LIT 0, %d{%s}\n' % (ind, self.source1)
        elif self.source1.isnumeric():
            code += 'PUSH %d{Immediate}\n' % int(self.source1)
        if self.is_variable(self.source2):
            ind = len(self.constant) + self.variable.index(self.source2) 
            code += 'LOD %d, %d{%s}\n' % (self.level, ind, self.source2)
        elif self.is_constant(self.source2):
            ind = self.constant.index(self.source2) 
            code += 'LIT 0, %d{%s}\n' % (ind, self.source2)
        elif self.is_intermediate(self.source2):
            ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.source2)
            del self.intermediate[self.intermediate.index(self.source2)]
            code += 'LIT 0, %d{%s}\n' % (ind, self.source2)
        elif self.source2.isnumeric():
             code += 'PUSH %d{Immediate}\n' % int(self.source2)
        code += 'OPR 0, <\n'
        if self.dest in self.variable:
            ind = len(self.constant) + self.variable.index(self.source1)
            code += 'STO %d, %d{%s}\n' % (self.level, ind, self.dest)
        elif 'temp' in self.dest:
            if len(self.intermediate) > 2:
                print('error length intermediate')
            self.intermediate.append(self.dest)
            ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.dest)
            code += 'STO %d, %d{%s}\n' % (self.level, ind, self.dest) 
        self.code.append(code)
        return True

    def below_equal(self):
        '''小于等于的条件操作'''
        code = ''
        if self.is_variable(self.source1):
            ind = len(self.constant) + self.variable.index(self.source1) 
            code += 'LOD %d, %d{%s}\n' % (self.level, ind, self.source1)
        elif self.is_intermediate(self.source1):
            ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.source1)
            del self.intermediate[self.intermediate.index(self.source1)]
            code += 'LIT 0, %d{%s}\n' % (ind, self.source1)
        elif self.is_constant(self.source1):
            ind = self.constant.index(self.source1) 
            code += 'LIT 0, %d{%s}\n' % (ind, self.source1)
        elif self.source1.isnumeric():
            code += 'PUSH %d{Immediate}\n' % int(self.source1)
        if self.is_variable(self.source2):
            ind = len(self.constant) + self.variable.index(self.source2) 
            code += 'LOD %d, %d{%s}\n' % (self.level, ind, self.source2)
        elif self.is_constant(self.source2):
            ind = self.constant.index(self.source2) 
            code += 'LIT 0, %d{%s}\n' % (ind, self.source2)
        elif self.is_intermediate(self.source2):
            ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.source2)
            del self.intermediate[self.intermediate.index(self.source2)]
            code += 'LIT 0, %d{%s}\n' % (ind, self.source2)
        elif self.source2.isnumeric():
             code += 'PUSH %d{Immediate}\n' % int(self.source2)
        code += 'OPR 0, <=\n'
        if self.dest in self.variable:
            ind = len(self.constant) + self.variable.index(self.source1)
            code += 'STO %d, %d{%s}\n' % (self.level, ind, self.dest)
        elif 'temp' in self.dest:
            if len(self.intermediate) > 2:
                print('error length intermediate')
            self.intermediate.append(self.dest)
            ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.dest)
            code += 'STO %d, %d{%s}\n' % (self.level, ind, self.dest) 
        self.code.append(code)
        return True

    def above(self):
        '''大于的条件操作'''
        code = ''
        if self.is_variable(self.source1):
            ind = len(self.constant) + self.variable.index(self.source1) 
            code += 'LOD %d, %d{%s}\n' % (self.level, ind, self.source1)
        elif self.is_intermediate(self.source1):
            ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.source1)
            del self.intermediate[self.intermediate.index(self.source1)]
            code += 'LIT 0, %d{%s}\n' % (ind, self.source1)
        elif self.is_constant(self.source1):
            ind = self.constant.index(self.source1) 
            code += 'LIT 0, %d{%s}\n' % (ind, self.source1)
        elif self.source1.isnumeric():
            code += 'PUSH %d{Immediate}\n' % int(self.source1)
        if self.is_variable(self.source2):
            ind = len(self.constant) + self.variable.index(self.source2) 
            code += 'LOD %d, %d{%s}\n' % (self.level, ind, self.source2)
        elif self.is_constant(self.source2):
            ind = self.constant.index(self.source2) 
            code += 'LIT 0, %d{%s}\n' % (ind, self.source2)
        elif self.is_intermediate(self.source2):
            ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.source2)
            del self.intermediate[self.intermediate.index(self.source2)]
            code += 'LIT 0, %d{%s}\n' % (ind, self.source2)
        elif self.source2.isnumeric():
             code += 'PUSH %d{Immediate}\n' % int(self.source2)
        code += 'OPR 0, >\n'
        if self.dest in self.variable:
            ind = len(self.constant) + self.variable.index(self.source1)
            code += 'STO %d, %d{%s}\n' % (self.level, ind, self.dest)
        elif 'temp' in self.dest:
            if len(self.intermediate) > 2:
                print('error length intermediate')
            self.intermediate.append(self.dest)
            ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.dest)
            code += 'STO %d, %d{%s}\n' % (self.level, ind, self.dest) 
        self.code.append(code)
        return True

    def above_equal(self):
        '''大于等于的条件操作'''
        code = ''
        if self.is_variable(self.source1):
            ind = len(self.constant) + self.variable.index(self.source1) 
            code += 'LOD %d, %d{%s}\n' % (self.level, ind, self.source1)
        elif self.is_intermediate(self.source1):
            ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.source1)
            del self.intermediate[self.intermediate.index(self.source1)]
            code += 'LIT 0, %d{%s}\n' % (ind, self.source1)
        elif self.is_constant(self.source1):
            ind = self.constant.index(self.source1) 
            code += 'LIT 0, %d{%s}\n' % (ind, self.source1)
        elif self.source1.isnumeric():
            code += 'PUSH %d{Immediate}\n' % int(self.source1)
        if self.is_variable(self.source2):
            ind = len(self.constant) + self.variable.index(self.source2) 
            code += 'LOD %d, %d{%s}\n' % (self.level, ind, self.source2)
        elif self.is_constant(self.source2):
            ind = self.constant.index(self.source2) 
            code += 'LIT 0, %d{%s}\n' % (ind, self.source2)
        elif self.is_intermediate(self.source2):
            ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.source2)
            del self.intermediate[self.intermediate.index(self.source2)]
            code += 'LIT 0, %d{%s}\n' % (ind, self.source2)
        elif self.source2.isnumeric():
             code += 'PUSH %d{Immediate}\n' % int(self.source2)
        code += 'OPR 0, >=\n'
        if self.dest in self.variable:
            ind = len(self.constant) + self.variable.index(self.source1)
            code += 'STO %d, %d{%s}\n' % (self.level, ind, self.dest)
        elif 'temp' in self.dest:
            if len(self.intermediate) > 2:
                print('error length intermediate')
            self.intermediate.append(self.dest)
            ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.dest)
            code += 'STO %d, %d{%s}\n' % (self.level, ind, self.dest) 
        self.code.append(code)
        return True

    def negation(self):
        '''非的条件操作'''
        pass

    switch_operation = {#以后再进行编号
        '+': add,
        '-': sub,
        '*': mul, 
        '/': div, 
        ':=': evaluation, 
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

    def declaration (self):
        '''处理声明语句'''
        if self.operator == 'var':
            if self.source1 in self.constant:
                ind = self.constant.index(self.source1)
                del self.constant[ind]
                self.variable.append(self.source1)
        elif self.operator == 'const':
            if self.source1 in self.variable:
                ind = self.variable.index(self.source1)
                del self.variable[ind]
                self.constant.append(self.source1)
            elif self.source1 not in self.constant:
                self.constant.append(self.source1)
        self.code.append('')
        return True

    def jmp_name(self):
        '''产生随机jmp使用的名字'''
        string = ''
        for i in range(7):
            string += random.choice('abcdefghijklmnoprstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')
        if string in list(self.jmp_nam.values()):
            string = self.jmp_name()
        return string

    def jmp(self):
        '''处理无条件跳转'''
        if self.dest not in self.jmp_nam.keys():
            print('error index %s: jump fault "%s", 006' % (str([self.operator,self.source1,self.source2,self.dest]), self.dest), end='\n\n')
            return False
        ind = 'ADDRESS' + str(list(self.jmp_nam.keys()).index(self.dest))
        code = 'JMP 0, %s\n' % (ind)
        self.code.append(code)
        return True

    def jcc(self):
        '''处理有条件跳转'''
        operation = self.operator[1:]
        code = ''
        if self.is_variable(self.source1):
            ind = len(self.constant) + self.variable.index(self.source1) 
            code += 'LOD %d, %d{%s}\n' % (self.level, ind, self.source1)
        elif self.is_intermediate(self.source1):
            ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.source1)
            del self.intermediate[self.intermediate.index(self.source1)]
            code += 'LIT 0, %d{%s}\n' % (ind, self.source1)
        elif self.is_constant(self.source1):
            ind = self.constant.index(self.source1) 
            code += 'LIT 0, %d{%s}\n' % (ind, self.source1)
        elif self.source1.isnumeric():
            code += 'PUSH %d{Immediate}\n' % int(self.source1)
        if self.is_variable(self.source2):
            ind = len(self.constant) + self.variable.index(self.source2) 
            code += 'LOD %d, %d{%s}\n' % (self.level, ind, self.source2)
        elif self.is_constant(self.source2):
            ind = self.constant.index(self.source2) 
            code += 'LIT 0, %d{%s}\n' % (ind, self.source2)
        elif self.is_intermediate(self.source2):
            ind = len(self.constant) + len(self.variable) + self.intermediate.index(self.source2)
            del self.intermediate[self.intermediate.index(self.source2)]
            code += 'LIT 0, %d{%s}\n' % (ind, self.source2)
        elif self.source2.isnumeric():
             code += 'PUSH %d{Immediate}\n' % int(self.source2)
        code += 'OPR 0, %s\n' % operation
        if self.dest not in self.jmp_nam.keys():
            print('error index %s: jcc fault "%s", 007' % (str([self.operator,self.source1,self.source2,self.dest]), self.dest), end='\n\n')
            return False
        ind = 'ADDRESS' + str(list(self.jmp_nam.keys()).index(self.dest))
        code += 'JPC 0, %s\n' % (ind)
        self.code.append(code)
        return True

    def insert_jmpname(self):
        '''插入跳转的位置的名称'''
        for element in list(self.jmp_nam.keys()):
            print(element)
            print(self.code[int(element)-1], '\n', self.code[int(element)], '\n', self.code[int(element)+1])
            self.code[int(element) + 1] = self.jmp_nam[element] + ':\t' + self.code[int(element) + 1]
        self.code_str = "".join(self.code)
        List = self.code_str.split('\n')
        List.pop()
        for element in list(self.jmp_nam.keys()):
            string = 'ADDRESS' + str(list(self.jmp_nam.keys()).index(element))
            ind_jmp = int()
            for j in range(len(List)):
                if self.jmp_nam[element] in List[j]:
                    ind_jmp = j
            for i in range(len(List)):
                ind_ = 0
                if string in List[i]:
                    ind = i
                else:
                    continue
                if not List[i].find('JPC') == -1:
                    code = 'JPC 0, %d{%s}' % (ind_jmp, self.jmp_nam[element])
                    List[i] = List[i][:List[i].find('JPC')] + code
                else:
                    code = 'JMP 0, %d{%s}' % (ind_jmp, self.jmp_nam[element])
                    List[i] = List[i][:List[i].find('JMP')] + code
        call_dest = dict()
        for element in list(self.level_fourEle.keys()):
            keyword1 = element + ':'
            for i in range(len(List)):
                if keyword1 in List[i]:
                    call_dest[element] = i
        for i in range(len(List)):
            if 'CALL' in List[i]:
                ind = List[i].find(', ') + 2            
                List[i] = List[i][:ind] + str(call_dest[List[i][ind:].replace('\n', '')]) + '{%s}' % List[i][ind:].replace('\n', '')
            pass
        self.code = List

    def write(self):
        '''处理写操作'''
        code=""
        if self.source1 in self.variable:
            ind = len(self.constant)+self.variable.index(self.source1)
            code = 'LOD 0, %d\n' % (ind)
        elif self.source1 in self.constant:
            ind = self.constant.index(self.source1)
            code = 'LOD 0, %d\n' % (ind)
        code += 'WRT 0, 0\n'
        self.code.append(code)
        return True

    def read(self):
        '''处理读操作'''
        if self.source1 in self.variable:
            ind = len(self.constant) + self.variable.index(self.source1)
            code = 'RED %d, %d{%s}\n' % (self.level, ind, self.source1)
            self.code.append(code)
            return True
        else :
            print('error index %s: The target of the read in operation is not a variable "%s", 005' % (str([self.operator,self.source1,self.source2,self.dest]), self.dest), end='\n\n')
            return False
        return False

    def call(self):
        if self.source1 in list(self.level_fourEle.keys()):
            self.code.append('CALL %d, %s\n' % (self.level, self.source1))
            self.level += 1
            return True
        else :
            print('error index %s: Undefined function name  "%s", 005' % (str([self.operator,self.source1,self.source2,self.dest]), self.source1), end='\n\n')
            return False
        return False


    switch_ = {
        'operation': operation, #OPR 0, a
        'declaration': declaration,#声明语句
        ##################################
        #'pushc': pushconstant,  #LIT 0, a
        #'pushv': pushvariable,  #LOD L, a
        #'pop': pop,             #STO L, a
        'call': call,           #CALL L, a<<<---TUDO
        #'inc': inc,             #INT 0, a
        'jmp': jmp,             #JMP 0, a
        'jcc': jcc,             #JPC 0, a
        'read': read,           #RED L, a
        'write': write,         #WRT 0, 0
        #############操作立即数############
        #                        #MOV [a], i
        #                        #PUSH i
        #############操作寄存器############
        #                        #MOV R, R/a
        #                        #PUSH R
        #                        #POP R
        ###########函数调用返回############
        #                        #RET
        #                        #NOP
        #                        #END
        ###################################
    }

    def call_code(self):
        ''''''
        for qwe in list(self.level_fourEle.keys()):
            #生成过程调用的初始代码
            code = '%s:\tPUSH EPX{Register}\n' % (qwe)+\
                   'PUSH EBX{Register}\n'+ \
                   'MOV EBX{Register}, ETX{Register}\n'
            self.code[-1] += code
            for element in self.level_fourEle[qwe]:
                self.operator = element[1]
                self.source1 = element[2]
                self.source2 = element[3]
                self.dest = element[4]
                self.No_ = element[0]
                if element[1] in ['+', '-', '*', '/', ':=', '==', '<', '<=', '>', '>=']:
                    case = 'operation'
                elif element[1] in ['var', 'const']:
                    case = 'declaration'
                elif element[1] == 'write':
                    case = 'write'
                elif element[1] == 'read':
                    case = 'read'
                elif element[1] == 'j':
                    case = 'jmp'
                elif element[1] in ['j>', 'j<', 'j>=', 'j<=', 'j==', 'j!=']:
                    case = 'jcc'
                elif element[1] == 'call':
                    case = 'call'
                elif element[1] == 'ret':
                    self.code.append('RET\n')
                    self.level -= 1
                    continue
                # 不合法字符，报错退出循环
                else:
                    print('error index %s: unkown character "%s", 001' % (str(element), element[1]), end='\n\n')
                    return False
                if not self.switch_[case](self):
                    print('error index %s: unkown character "%s", 002' % (str(element), element[1]), end='\n\n')
                    return False
        pass

    def midoutput(self):
        ''''''
        code = list(self.code)
        for element in range(len(self.code)):
            List1 = list()
            List2 = list()
            iterator1 = re.finditer('\{[a-zA-Z0-9]*\}', self.code[element])
            iterator2 = re.finditer('[a-zA-Z0-9]*:', self.code[element])
            for hut in iterator1:
                List1.append(hut.group())
            for hut in iterator2:
                List2.append(hut.group())
            if len(List1):
                for i in List1:
                    code[element] = code[element].replace(i, '')
            if len(List2):
                for i in List2:
                    if i[:-1] in list(self.level_fourEle.keys()):
                        code[element] = 'NOP'
                        code[element + 1] = 'NOP'
                        code[element + 2] = 'NOP'
                    else:
                        code[element] = code[element].replace(i, '')
        #print(code)
        with open(self.file_name + '_midcode'+'.txt', 'w') as f:
            f.write("\n".join(code).replace('\t', ''))
        pass

    def transform(self):
        '''由本函数进行转换操作，并将结果输出到"|filename|_output.txt"的文件中'''
        #初始化变量(将变量入栈)
        self.code = ['MOV EBX{Register}, 0{Immediate}\n'+\
                     'MOV ETX{Register}, EBX{Register}\n'+\
                     'INC 0, %s\n' % (len(self.variable)+ len(self.constant)+ 2 - 1)] #压栈了(先常后变)变量和两个存中间变量的空间

        #处理四元式
        self.operator = ''
        self.source1 = ''
        self.source2 = ''
        self.dest = ''
        call_level = 0
        call_name = ''
        for element in self.fourEle:
            if call_level == 0:
                self.operator = element[1]
                self.source1 = element[2]
                self.source2 = element[3]
                self.dest = element[4]
                self.No_ = element[0]
                if element[1] in ['+', '-', '*', '/', ':=', '==', '<', '<=', '>', '>=']:
                    case = 'operation'
                elif element[1] in ['var', 'const']:
                    case = 'declaration'
                elif element[1] == 'write':
                    case = 'write'
                elif element[1] == 'read':
                    case = 'read'
                elif element[1] == 'j':
                    case = 'jmp'
                elif element[1] in ['j>', 'j<', 'j>=', 'j<=', 'j==', 'j!=']:
                    case = 'jcc'
                elif element[1] == 'proc':
                    if element[2] in self.funcname:
                        call_level += 1
                        call_name = element[2]
                        self.level_fourEle[call_name] = list()
                        self.code.append('')
                        continue
                    else:
                        print('error index %s: unkown function name "%s", 001' % (str(element), element[2]), end='\n\n')
                        return False
                elif element[1] == 'call':
                    case = 'call'
                # 不合法字符，报错退出循环
                else:
                    print('error index %s: unkown character "%s", 001' % (str(element), element[1]), end='\n\n')
                    return False
                if not self.switch_[case](self):
                    print('error index %s: unkown character "%s", 002' % (str(element), element[1]), end='\n\n')
                    return False
            else:
                if element[1] == 'ret':
                    self.level_fourEle[call_name].append(element)
                    call_level -=1
                    self.code.append('')
                else:
                    self.level_fourEle[call_name].append(element)
                    self.code.append('')
        self.code[-1] = self.code[-1] + 'END\n'
        self.call_code()
        #输出目标机代码
        self.insert_jmpname()
        self.midoutput()
        self.code_str = "\n".join(self.code).replace('\t', '\n')
        with open(self.file_name + '_output'+'.txt', 'w') as f:
            f.write(self.code_str)
        pass
