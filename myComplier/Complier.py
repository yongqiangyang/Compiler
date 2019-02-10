import json
from pprint import pprint
from copy import deepcopy

"""
    本程序用于将PASCAL语言子集（PL/0）的源程序转化为四元式的中间代码
    词法分析技术：一遍遍历源程序，生成符号表
    语法分析技术：SLR
    语义分析技术：翻译模式
"""
#生成产生式
#与mySet_productions.py共同使用，将产生式输出到productions.txt文件中。
def write_productions_to_file(start, productions, path='productions.txt'):
    with open(path, 'w') as f:
        f.write(json.dumps(start) + '\n')
        f.write(json.dumps(productions) + '\n')


class Compiler:
    def __init__(self, sharp='#', point='.', acc='acc', productions_file='productions.txt'):
        # 终结符
        self.overs = set()
        # 保留字
        self.reserved = set()
        # 单目操作符
        self.one_op_set = set()
        # 双目操作符
        self.two_next = dict()

        with open(productions_file, 'r') as f:
            lines = f.readlines()
            self.start = json.loads(lines[0])
            self.productions = json.loads(lines[1])

        #设置非终结符、保留字等
        self.nonterminals = self.productions.keys()
        self.get_overs_reserved()

        #求文法的first集与Follow集
        self.sharp = sharp
        self.first = {nontermainal: {} for nontermainal in self.nonterminals}
        self.follow = {nontermainal: set() for nontermainal in self.nonterminals}
        self.get_first_follow()

        # 计算文法项目
        self.new_start = self.start + "'"
        self.point = point
        self.items = {key: list() for key in self.nonterminals}
        self.get_items()

        # 计算文法的状态和分析表
        self.status_list = [
            self.closure([(self.new_start, [self.point, self.start])]), ]
        self.analyse_table = dict()
        self.acc = acc
        self.get_analyse_table()

    #设置终结符、保留字等
    def get_overs_reserved(self):
        for nonterminal in self.nonterminals:
            for right in self.productions[nonterminal]:
                for sign in right:
                    if sign not in self.nonterminals and len(sign) > 0:
                        #终结符集合
                        self.overs.add(sign)
                        #识别双目操作符，比如：！=  <= >=
                        if len(sign) >= 2 and not sign[0].isalpha():
                            if sign[0] in self.two_next.keys():
                                self.two_next[sign[0]].add(sign[1:])
                            else:
                                self.two_next[sign[0]] = {sign[1:], }
                        #识别保留字，比如and id num true
                        elif sign[0].isalpha():
                            self.reserved.add(sign)
                        #识别单目操作符，比如： + - * / （ ）
                        else:
                            self.one_op_set.add(sign)

        #将存在于双目操作符中的首字符的单目操作符删去，并在双目操作符中添加 空格
        remove_set = set()
        for sign in self.one_op_set:
            if sign[0] in self.two_next.keys():
                self.two_next[sign[0]].add('')
                remove_set.add(sign)
        for sign in remove_set:
            self.one_op_set.remove(sign)
        # print('reserved word set:')
        # pprint(self.reserved)
        # print('one_op_set:')
        # pprint(self.one_op_set)
        # print('two_next dict:')
        # pprint(self.two_next)

    #求文法的first集与Follow集
    def get_first_follow(self):
        # 求first第一轮，产生式右部首字符为终结符号
        self.first_first = list()
        for nontermainal in self.nonterminals:
            for right in self.productions[nontermainal]:
                if right[0] in self.overs:
                    self.first[nontermainal][right[0]] = right
                    self.first_first.append((nontermainal, right))
        # 求first第二轮
        while True:
            old_first = deepcopy(self.first)
            for nontermainal in self.nonterminals:
                new_dict = {}
                for right in self.productions[nontermainal]:
                    if (nontermainal, right) in self.first_first:
                        new_dict = self.first[nontermainal]
                        continue
                    if right[0] != '':
                        if right[0] in self.overs:
                            new_dict.update({right[0]: right})
                        else:
                            for sign in right:
                                if sign in self.nonterminals:
                                    first_ = self.first[sign]
                                    new_dict.update({key: right for key in first_.keys()})
                                    if '' not in first_.keys():
                                        break
                    else:
                        new_dict.update({'': ''})
                self.first[nontermainal].update(new_dict)
            if old_first == self.first:
                break
        # 起始符号follow集
        self.follow[self.start].add(self.sharp)
        # 循环直到follow集不再变化
        while True:
            old_follow = deepcopy(self.follow)
            for nontermainal in self.nonterminals:
                for right in self.productions[nontermainal]:
                    if right[0] == '':
                        continue
                    for i, sign in enumerate(right):
                        if sign in self.overs:
                            continue
                        if i == len(right) - 1:
                            self.follow[sign] |= self.follow[nontermainal]
                        elif right[i + 1] in self.overs:
                            self.follow[sign].add(right[i + 1])
                        else:
                            next_set = {key for key in self.first[right[i + 1]].keys()}
                            next_set_without_null = {key for key in self.first[right[i + 1]].keys() if key != ''}
                            self.follow[sign] |= next_set_without_null
                            if '' in next_set:
                                self.follow[sign] |= self.follow[nontermainal]
            if old_follow == self.follow:
                break

    #得到项目
    def get_items(self):
        self.items[self.new_start] = [[self.point, self.start], [self.start, self.point]]
        for nonterminal in self.nonterminals:
            for right in self.productions[nonterminal]:
                if right[0] == '':
                    self.items[nonterminal].append([self.point, ])
                    continue
                for i in range(len(right)):
                    self.items[nonterminal].append(
                        right[:i] + [self.point, ] + right[i:]
                    )
                self.items[nonterminal].append(right + [self.point, ])
        print("项目集：")
        pprint(self.items)

    # 递归求解输入项目集合的闭包
    def closure(self, production_list):
        ret = production_list.copy()
        # 对于每一个项目，找到分隔符，如果后面有非终结符号，执行闭包操作
        for production in production_list:
            right = production[1]
            i = 0
            while i < len(right) and right[i] != self.point:
                i += 1
            if i + 1 < len(right) and right[i + 1] in self.nonterminals:
                for item in self.items[right[i + 1]]:
                    if self.point == item[0] and (right[i + 1], item) not in ret:
                        ret.append((right[i + 1], item))
        if ret == production_list:
            return ret
        else:
            return self.closure(ret)

    # 实现go函数
    def go(self, production_list, sign):
        new_production_list = list()
        # 找到接受sign的项目，将分隔符后移一位
        for production in production_list:
            right = production[1]
            i = 0
            while i < len(right) and right[i] != self.point:
                i += 1
            if i + 1 < len(right) and right[i + 1] == sign:
                new_right = list(right)
                temp = new_right[i]
                new_right[i] = new_right[i + 1]
                new_right[i + 1] = temp
                if (production[0], new_right) not in new_production_list:
                    new_production_list.append((production[0], new_right))
                i += 1
        # 返回新的状态的闭包
        return self.closure(new_production_list)

    # 求解项目集与分析表
    def get_analyse_table(self):
        # last_index指示现有状态集个数
        # index是正在分析的状态的索引
        last_index = 0
        index = 0
        while True:
            # 首先得到该状态接受的符号及其对应项目
            receive_sign_dict = {}
            # 遍历状态集中的每一个项目
            for (left, right) in self.status_list[index]:
                # 找到分隔符
                i = 0
                while i < len(right) and right[i] != self.point:
                    i += 1
                # 如果分隔符不在末尾，将则其后的符号为接受符号
                if i + 1 < len(right):
                    if right[i + 1] not in receive_sign_dict.keys():
                        receive_sign_dict[right[i + 1]] = [(left, right)]
                    elif (left, right) not in receive_sign_dict[right[i + 1]]:
                        receive_sign_dict[right[i + 1]].append((left, right))
                # 如果分隔符在末尾
                else:
                    # 如果左部为拓广文法起始符号，则记录acc
                    if left == self.new_start:
                        self.analyse_table[index] = {self.sharp: [self.acc, ]}
                    # 否则找到对应的产生式
                    else:
                        production_index = 0
                        for left_ in self.nonterminals:
                            for right_ in self.productions[left_]:
                                new_right = deepcopy(right)
                                new_right.remove(self.point)
                                if (left, new_right) == (left_, right_):
                                    # 根据左部的follow集将r填入分析表
                                    self.analyse_table[index] = {
                                        over: [production_index, 'r', (left_, right_)]
                                        for over in (self.follow[left_])
                                    }
                                production_index += 1
            # 遍历接受符号
            for sign, production_set in receive_sign_dict.items():
                # 用函数go求出新的状态
                new_status = self.go(production_set, sign)
                new_action = []
                # 如果新状态没有和已有的状态重复，将其加入状态列表
                if new_status not in self.status_list:
                    self.status_list.append(new_status)
                    last_index += 1
                    new_action.append(last_index)
                else:
                    new_action.append(self.status_list.index(new_status))
                # 更新分析表
                for production in production_set:
                    new_action.append(production)
                if index not in self.analyse_table.keys():
                    self.analyse_table[index] = {sign: new_action}
                else:
                    self.analyse_table[index].update({sign: new_action})
            index += 1
            # 如果没有状态可以分析，结束循环
            if index > last_index:
                break
        # print('stauts list:')
        # pprint(self.status_list)
        print('analyse table:')
        pprint(self.analyse_table)

    # 词法分析函数
    # 检查是否为保留字
    def lookup(self):
        return True if self.token in self.reserved else False

    # 记录tag与string，清空token
    def out(self, c=''):
        if(self.token=='else'):
            self.tag_list.append(':')
            self.string_list.append(':')
        self.tag_list.append(self.token if c == '' else c)
        self.string_list.append(self.token)
        if(self.token=='then' or self.token=='else' or self.token=='while' or self.token=='do'):
            self.tag_list.append(':')
            self.string_list.append(':')
        self.token = ''

    # 读取下一个输出符号，没有返回False
    def get_char(self):
        if self.index == len(self.raw_string):
            return False
        self.ch = self.raw_string[self.index]
        self.token += self.ch
        self.index += 1
        return self.ch

    # 回退一个符号
    def retract(self):
        self.index = max(self.index - 1, 0)
        self.ch = self.raw_string[max(self.index - 1, 0)]
        self.token = self.token[:-1]

    # 如果是字母，循环调用get_char，最后调用out
    def alpha(self):
        while self.index < len(self.raw_string) and self.raw_string[self.index].isalnum() and self.get_char():
            pass
        self.out('' if self.lookup() else 'id')
        return True

    # 如果是数字，循环调用get_char，最后调用out
    def digit(self):
        while self.index < len(self.raw_string) and self.raw_string[self.index].isdigit() and self.get_char():
            pass
        self.out('integer')
        return True

    # 如果是单符号终结符，直接调用out
    def one_op(self):
        self.out()
        return True

    # 如果可能是多符号终结符，先判断后一个是不是，不是回退
    def two_op(self):
        now_ch = self.ch
        if self.get_char() not in self.two_next[now_ch]:
            self.retract()
        self.out()
        return True

    # 如果是空格，清空token
    def blank(self):
        self.token = ''
        return True

    switch = {
        'alpha': alpha,
        'digit': digit,
        'one_op': one_op,
        'two_op': two_op,
        'blank': blank
    }

    #分析词法
    def analyse_cifa(self):
        self.token = ''
        self.index = 0
        self.ch = ''
        self.tag_list = []
        self.string_list = []

        while self.get_char():
            if self.ch == ' ':
                case = 'blank'
            elif self.ch.isalpha():
                case = 'alpha'
            elif self.ch.isdigit():
                case = 'digit'
            elif self.ch in self.one_op_set:
                case = 'one_op'
            elif self.ch in self.two_next.keys():
                case = 'two_op'
            # 不合法字符，报错退出循环
            else:
                print('词法分析错误： 索引： %s: 不明字符： "%s"' % (self.index, self.ch), end='\n\n')
                return False
            # 词法分析出错，报错退出循环
            if not self.switch[case](self):
                print('词法分析错误： 索引： %s: 不明字符： "%s"' % (self.index, self.token), end='\n\n')
                return False
        with open(self.file_name + '.two', 'w') as f:
            for i in range(len(self.tag_list)):
                if i == len(self.tag_list)-1:
                    f.write('%s %s' %(self.string_list[i],self.tag_list[i]))
                else:
                    f.write('%s %s\n' %(self.string_list[i],self.tag_list[i]))
        return True

    #分析语法
    def analyse_yufa(self):
        print('grammar analyse:')
        # 初始化输入串列表、状态栈、符号栈
        self.tag_list += self.sharp
        string_index = 0
        status_stack = [0, ]
        sign_stack = [self.sharp, ]
        #初始化语义分析的四元式列表、分析栈
        siyuanshi_list = []
        siyuanshi_num=0
        temp_stack = []         #临时栈
        temp_index = 0          #临时栈索引
        lexp_truelist = []      #回填技术
        lexp_falselist = []     #回填技术
        M1_quad=[]              #回填技术
        M2_quad=[]              #回填技术
        N_nextlist=[]           #回填技术
        S_nextlist=[]           #回填技术
        # 不停分析直到接受
        while self.analyse_table[status_stack[-1]][self.tag_list[string_index]][0] != self.acc:
            # 如果不是r，则为s
            if 'r' != self.analyse_table[status_stack[-1]][self.tag_list[string_index]][1]:
                # push
                status_stack.append(self.analyse_table[status_stack[-1]][self.tag_list[string_index]][0])
                sign_stack.append(self.tag_list[string_index])
                if(self.tag_list[string_index]=='id'):
                    temp_stack.append(self.string_list[string_index])
                elif(self.tag_list[string_index]=='integer'):
                    temp_stack.append(self.string_list[string_index])

                # advance
                string_index += 1
                print(status_stack, sign_stack,temp_stack)
            else:
                # 为r，取出对应产生式的左部与右部
                left = self.analyse_table[status_stack[-1]][self.tag_list[string_index]][2][0]
                right = self.analyse_table[status_stack[-1]][self.tag_list[string_index]][2][1]
                # 语义分析，四元式
                # 分析运算符
                if any([i in right for i in ['+', '-', '*', '/']]):
                    op = right[1]
                    one = temp_stack[-2] if type(temp_stack[-2]) == str else 'temp%d' % temp_stack[-2]
                    two = temp_stack[-1] if type(temp_stack[-1]) == str else 'temp%d' % temp_stack[-1]
                    result = 'temp%d' % temp_index
                    siyuanshi_list.append([siyuanshi_num,op, one, two, result])
                    siyuanshi_num+=1
                    temp_stack.pop()
                    temp_stack.pop()
                    temp_stack.append(temp_index)
                    temp_index += 1
                # 分析赋值语句
                elif ':=' in right:
                    op = right[1]
                    one = temp_stack[-1] if type(temp_stack[-1]) == str else 'temp%d' % temp_stack[-1]
                    two = '_'
                    result = temp_stack[-2] if type(temp_stack[-2]) == str else 'temp%d' % temp_stack[-2]
                    siyuanshi_list.append([siyuanshi_num,op, one, two, result])
                    siyuanshi_num+=1
                    S_nextlist.append(siyuanshi_num)
                    temp_stack.pop()
                    temp_stack.pop()
                # 分析逻辑运算符
                elif any([i in right for i in ['<','>','<=','>=','==','!=']]):
                    op = 'j'+right[1]
                    one = temp_stack[-2] if type(temp_stack[-2]) == str else 'temp%d' % temp_stack[-2]
                    two = temp_stack[-1] if type(temp_stack[-1]) == str else 'temp%d' % temp_stack[-1]
                    result=0
                    siyuanshi_list.append([siyuanshi_num,op, one, two, result])
                    lexp_truelist.append(siyuanshi_num)
                    siyuanshi_num += 1
                    op = 'j'
                    one ='_'
                    two ='_'
                    result = 0
                    siyuanshi_list.append([siyuanshi_num, op, one, two, result])
                    lexp_falselist.append(siyuanshi_num)
                    siyuanshi_num+=1
                    temp_stack.pop()
                    temp_stack.pop()
                # 分析while的一个条件
                elif 'lexp'==left and ['exp1']==right:
                    op = 'jnz'
                    one = temp_stack[-1] if type(temp_stack[-1]) == str else 'temp%d' % temp_stack[-1]
                    two = '_'
                    result = 0
                    siyuanshi_list.append([siyuanshi_num, op, one, two, result])
                    lexp_truelist.append(siyuanshi_num)
                    siyuanshi_num += 1
                    op = 'j'
                    one = '_'
                    two = '_'
                    result = 0
                    siyuanshi_list.append([siyuanshi_num, op, one, two, result])
                    lexp_falselist.append(siyuanshi_num)
                    siyuanshi_num += 1
                    temp_stack.pop()
                # 用于分析if_then if_then_else _while_do
                elif 'M1'==left and [':']==right:
                    M1_quad.append(siyuanshi_num)
                # 用于分析if_then if_then_else _while_do
                elif 'M2' == left and [':'] == right:
                    M2_quad.append(siyuanshi_num)
                # 用于分析if_then if_then_else _while_do
                elif 'N'==left and [':']==right:
                    op = 'j'
                    one = '_'
                    two = '_'
                    result = '_'
                    siyuanshi_list.append([siyuanshi_num, op, one, two, result])
                    N_nextlist.append(siyuanshi_num)
                    siyuanshi_num += 1
                # 用于分析if_then
                elif ['if','lexp','then','M1','statement']==right:
                    siyuanshi_list[lexp_truelist[-1]][4]=M1_quad[-1]
                    siyuanshi_list[lexp_falselist[-1]][4]=S_nextlist[-1]
                    lexp_truelist.pop()
                    M1_quad.pop()
                    lexp_falselist.pop()
                # 用于分析if_then_else
                elif ['if','lexp','then','M1','statement','N','else','M2','statement']==right:
                    siyuanshi_list[lexp_truelist[-1]][4] = M1_quad[-1]
                    siyuanshi_list[lexp_falselist[-1]][4] = M2_quad[-1]
                    siyuanshi_list[N_nextlist[-1]][4] = S_nextlist[-1]
                    lexp_truelist.pop()
                    M1_quad.pop()
                    M2_quad.pop()
                    lexp_falselist.pop()
                    N_nextlist.pop()
                # 用于分析while_do
                elif ['while','M1','lexp','do','M2','statement']==right:
                    op = 'j'
                    one = '_'
                    two = '_'
                    result =M1_quad[-1]
                    siyuanshi_list.append([siyuanshi_num, op, one, two, result])
                    siyuanshi_num+=1
                    siyuanshi_list[lexp_truelist[-1]][4] = M2_quad[-1]
                    siyuanshi_list[lexp_falselist[-1]][4] = S_nextlist[-1]+1
                    S_nextlist.append(siyuanshi_num)
                    M1_quad.pop()
                    lexp_truelist.pop()
                    M2_quad.pop()
                    lexp_falselist.pop()

                # 分析读入操作
                elif 'id1' == left:
                    op = 'read'
                    one = temp_stack[-1] if type(temp_stack[-1]) == str else 'temp%d' % temp_stack[-1]
                    two = '_'
                    result ='_'
                    siyuanshi_list.append([siyuanshi_num, op, one, two, result])
                    siyuanshi_num += 1
                    S_nextlist.append(siyuanshi_num)
                    temp_stack.pop()

                #分析写出操作
                elif 'exp' == left:
                    op = 'write'
                    one = temp_stack[-1] if type(temp_stack[-1]) == str else 'temp%d' % temp_stack[-1]
                    two = '_'
                    result = '_'
                    siyuanshi_list.append([siyuanshi_num, op, one, two, result])
                    siyuanshi_num += 1
                    S_nextlist.append(siyuanshi_num)
                    temp_stack.pop()

                #分析调用操作
                elif 'statement' == left and (['call','id','(','call1',')'] == right or ['call','id','(',')'] == right):
                    op = 'call'
                    one = temp_stack[-1] if type(temp_stack[-1]) == str else 'temp%d' % temp_stack[-1]
                    two = '_'
                    result = '_'
                    siyuanshi_list.append([siyuanshi_num, op, one, two, result])
                    siyuanshi_num += 1
                    S_nextlist.append(siyuanshi_num)

                #分析调用操作
                elif 'call1'==left:
                    op = 'param'
                    one = temp_stack[-1]
                    two = '_'
                    result = '_'
                    siyuanshi_list.append([siyuanshi_num, op, one, two, result])
                    siyuanshi_num += 1
                    temp_stack.pop()

                # 分析声明变量操作
                elif 'vardecl2' == left:
                    op = 'var'
                    one = temp_stack[-1] if type(temp_stack[-1]) == str else 'temp%d' % temp_stack[-1]
                    two = '_'
                    result = '_'
                    siyuanshi_list.append([siyuanshi_num, op, one, two, result])
                    siyuanshi_num += 1
                    temp_stack.pop()

                #分析子过程
                elif 'proc1' == left:
                    op = 'ret'
                    one = '_'
                    two = '_'
                    result = '_'
                    siyuanshi_list.append([siyuanshi_num, op, one, two, result])
                    siyuanshi_num += 1

                # 分析子过程
                elif 'proc2' == left:
                    temp_stack.pop()

                # 分析子过程
                elif 'M3' == left and [';' ] == right:
                    op = 'proc'
                    one = temp_stack[-1] if type(temp_stack[-1]) == str else 'temp%d' % temp_stack[-1]
                    two = '_'
                    result = '_'
                    siyuanshi_list.append([siyuanshi_num, op, one, two, result])
                    siyuanshi_num += 1
                    temp_stack.pop()

                # 语义分析结束
                # pop(第i个产生式右部文法符号的个数)
                for i in range(len(right)):
                    sign_stack.pop()
                    status_stack.pop()
                print(status_stack, sign_stack,temp_stack)
                # push(GOTO[新的栈顶状态][第i个产生式的左部])
                status_stack.append(self.analyse_table[status_stack[-1]][left][0])
                sign_stack.append(left)
                print(status_stack, sign_stack,temp_stack)

            # error，退出循环
            if self.tag_list[string_index] not in self.analyse_table[status_stack[-1]].keys():
                print('语法分析错误：', string_index, self.tag_list[string_index], status_stack[-1])
                return False
        print("四元式：")
        pprint(siyuanshi_list)
        with open(self.file_name + '.four', 'w') as f:
            for i in range(len(siyuanshi_list)):
                if i == len(siyuanshi_list)-1:
                    f.write('%s %s %s %s %s' % (siyuanshi_list[i][0], siyuanshi_list[i][1], siyuanshi_list[i][2], siyuanshi_list[i][3], siyuanshi_list[i][4]))
                else:
                    f.write('%s %s %s %s %s\n' % (
                    siyuanshi_list[i][0], siyuanshi_list[i][1], siyuanshi_list[i][2], siyuanshi_list[i][3],
                    siyuanshi_list[i][4]))

        print('ok')
        return True


    #词法分析&&语法分析
    def analyse(self, file):
        raw_string = open(file, 'r').read()
        #源程序预处理
        self.raw_string = raw_string.replace('\t', '')
        self.raw_string = self.raw_string.replace('\n', ' ')
        self.file_name = file[ :file.rindex('.')]

        self.analyse_cifa() and self.analyse_yufa()


if __name__ == '__main__':
     analyzer = Compiler()
     analyzer.analyse("test1.txt")