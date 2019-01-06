from pprint import pprint
from copy import deepcopy


class SLRAnalyzer:
    def __init__(self, start, productions, new_start='S', point='.', sharp='#',acc='acc',log_level=0):
        # 接受参数
        self.start = start
        self.new_start = new_start
        self.productions = productions
        self.nonterminals = productions.keys()
        self.log_level = log_level
        self.point = point

        # 计算文法终结符号
        self.overs = set()
        self.get_overs()

        # 计算文法follow集
        self.sharp = sharp
        self.first = {nontermainal: {} for nontermainal in self.nonterminals}
        self.follow = {nontermainal: set() for nontermainal in self.nonterminals}
        self.get_first_follow()

        # 计算文法项目
        self.items = {key: list() for key in self.nonterminals}
        self.get_items()

        # 计算文法的状态和分析表
        self.status_list = [self.closure({(self.new_start, self.point + self.start)}), ]
        self.analyse_table = dict()
        self.acc = acc
        self.get_analyse_table()

        # 判断文法类型
        self.language_type = self.get_language_type()
        if self.language_type not in [0, 1]:
            exit('unsupported language!')

    # 求解文法的非终结符号集，即产生式右部不是非终结符号的符号
    def get_overs(self):
        for nonterminal in self.nonterminals:
            for right in self.productions[nonterminal]:
                for sign in right:
                    if sign not in self.nonterminals:
                        self.overs.add(sign)
        if self.log_level >= 2:
            print('over sign set:')
            pprint(self.overs)

    # 求first集和follow集
    def get_first_follow(self):
        # 求first第一轮，产生式右部首字符为终结符号
        self.first_first = set()
        for nontermainal in self.nonterminals:
            for right in self.productions[nontermainal]:
                if right != '' and right[0] in self.overs:
                    self.first[nontermainal][right[0]] = right
                    self.first_first.add((nontermainal, right))
        # 求first第二轮
        while True:
            old_first = deepcopy(self.first)
            for nontermainal in self.nonterminals:
                new_dict = {}
                for right in self.productions[nontermainal]:
                    if (nontermainal, right) in self.first_first:
                        new_dict = self.first[nontermainal]
                        continue
                    if right != '':
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
        if self.log_level >= 2:
            print('follow set:')
            pprint(self.follow)

    def get_items(self):
        self.items[self.new_start] = [self.point + self.start, self.start + self.point]
        for nonterminal in self.nonterminals:
            for right in self.productions[nonterminal]:
                for i in range(len(right)):
                    self.items[nonterminal].append(right[:i] + self.point + right[i:])
                self.items[nonterminal].append(right + self.point)
        if self.log_level >= 2:
            print('items:')
            pprint(self.items)

    # 递归求解输入项目集合的闭包
    def closure(self, production_set):
        ret = production_set.copy()
        # 对于每一个项目，找到分隔符，如果后面有非终结符号，执行闭包操作
        for production in production_set:
            right = production[1]
            i = 0
            while i < len(right) and right[i] != self.point:
                i += 1
            if i + 1 < len(right) and right[i + 1] in self.nonterminals:
                for item in self.items[right[i + 1]]:
                    if self.point == item[0]:
                        ret.add((right[i + 1], item))
        if ret == production_set:
            return ret
        else:
            return self.closure(ret)

    # 实现go函数
    def go(self, production_set, sign):
        new_production_set = set()
        # 找到接受sign的项目，将分隔符后移一位
        for production in production_set:
            right = production[1]
            i = 0
            while i < len(right) and right[i] != self.point:
                i += 1
            if i + 1 < len(right) and right[i + 1] == sign:
                new_right = list(right)
                temp = new_right[i]
                new_right[i] = new_right[i + 1]
                new_right[i + 1] = temp
                new_production_set.add((production[0], ''.join(new_right)))
                i += 1
        # 返回新的状态的闭包
        return self.closure(new_production_set)

    # 模拟人求解状态集的过程，求解项目集与分析表
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
                        receive_sign_dict[right[i + 1]] = {(left, right)}
                    else:
                        receive_sign_dict[right[i + 1]].add((left, right))
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
                                if (left, right.replace(self.point, '')) == (left_, right_):
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
                # 如果新状态没有和已有的状态重复，讲起加入状态列表
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
        if self.log_level >= 1:
            print('stauts list:')
            pprint(self.status_list)
            print('analyse table:')
            pprint(self.analyse_table)

    # 通过项目集分析文法类型
    def get_language_type(self):
        ret = 1
        for status in self.status_list:
            guiyue_items = list()
            yijin_items = list()
            # 遍历一个状态中的所有项目
            for left, right in status:
                # 找到分隔符号，记录归约项目的follow集和移进项目的终结符号
                i = 0
                while i < len(right) and right[i] != self.point:
                    i += 1
                if i + 1 == len(right):
                    if right[i - 1] != self.new_start and left != self.new_start:
                        guiyue_items.append(self.follow[left])
                elif right[i + 1] in self.overs:
                    yijin_items.append(right[i + 1])
            # 如果有归约归约冲突或移进归约冲突
            if len(guiyue_items) >= 2 or len(guiyue_items) > 0 and len(yijin_items) > 0:
                # 至少为slr1文法，置ret=0
                ret = 0
                # 判断能否用follow集解决冲突
                # 不能解决，返回-1
                jihe = set()
                for nonterminal in guiyue_items:
                    if nonterminal in jihe:
                        return -1
                    else:
                        jihe |= nonterminal
                for sign in yijin_items:
                    if sign in jihe:
                        return -1
                    else:
                        jihe.add(sign)
        return ret

    # 词法分析
    # 检查是否为保留字
    def lookup(self):
        return True if self.token in self.reserved else False

    # 记录tag与string，清空token
    def out(self, c=''):
        self.tag_list.append(self.token if c == '' else c)
        self.string_list.append(self.token)
        self.token = ''

    # 读取下一个输出符号，没有返回False
    def get_char(self):
        if self.index == len(self.string):
            return False
        self.ch = self.string[self.index]
        self.token += self.ch
        self.index += 1
        return self.ch

    # 回退一个符号
    def retract(self):
        self.index = max(self.index - 1, 0)
        self.ch = self.string[max(self.index - 1, 0)]
        self.token = self.token[:-1]

    # 如果是字母，循环调用get_char，最后调用out
    def alpha(self):
        while self.index < len(self.string) and self.string[self.index].isalnum() and self.get_char():
            pass
        self.out('' if self.lookup() else 'i')
        return True

    # 如果是数字，循环调用get_char，最后调用out
    def digit(self):
        while self.index < len(self.string) and self.string[self.index].isdigit() and self.get_char():
            pass
        self.out('i')
        return True

    # 如果是单符号终结符，直接调用out
    def one(self):
        self.out()
        return True

    # 如果是双符号终结符，调用get_char后决定是否回退
    def two(self):
        now_ch = self.ch
        if self.get_char() not in self.two_next[now_ch]:
            self.retract()
        if self.token in self.token_to_category:
            self.out(self.token_to_category[self.token])
            return True
        return False

    switch = {
        'alpha': alpha,
        'digit': digit,
        'one': one,
        'two': two,
    }

    # lr语法分析器
    def analyse_lr(self):
        # 初始化输入串列表、状态栈、符号栈
        self.tag_list += self.sharp
        string_index = 0
        status_stack = [0, ]
        sign_stack = [self.sharp, ]
        # 初始化语义分析的四元式列表、分析栈
        siyuanshi_list = []
        temp_stack = []
        temp_index = 0
        # 不停分析直到接受
        while self.analyse_table[status_stack[-1]][self.tag_list[string_index]][0] != self.acc:
            # 如果不是r，则为s
            if 'r' != self.analyse_table[status_stack[-1]][self.tag_list[string_index]][1]:
                if self.log_level >= 1:
                    print(status_stack, sign_stack)
                # push()
                status_stack.append(self.analyse_table[status_stack[-1]][self.tag_list[string_index]][0])
                sign_stack.append(self.tag_list[string_index])
                temp_stack.append(self.tag_list[string_index])
                # advance()
                string_index += 1
            else:
                # 为r，取出对应产生式的左部与右部
                left = self.analyse_table[status_stack[-1]][self.tag_list[string_index]][2][0]
                right = self.analyse_table[status_stack[-1]][self.tag_list[string_index]][2][1]
                # 语义分析，四元式
                if any([i in right for i in ['+', '-', '*', '/']]):
                    op = right[1]
                    one = temp_stack[-2] if type(temp_stack[-2]) == str else 'temp%d' % temp_stack[-2]
                    two = temp_stack[-1] if type(temp_stack[-1]) == str else 'temp%d' % temp_stack[-1]
                    result = 'temp%d' % temp_index
                    siyuanshi_list.append((op, one, two, result))
                    temp_stack.pop()
                    temp_stack.pop()
                    temp_stack.append(temp_index)
                    temp_index += 1
                elif '=' in right:
                    op = right[1]
                    one = temp_stack[-1] if type(temp_stack[-1]) == str else 'temp%d' % temp_stack[-1]
                    two = '_'
                    result = temp_stack[-2] if type(temp_stack[-2]) == str else 'temp%d' % temp_stack[-2]
                    siyuanshi_list.append((op, one, two, result))
                    temp_stack.pop()
                    temp_stack.append(temp_index)
                    temp_index += 1
                elif right == 'i':
                    temp_stack.append(self.string_list[string_index - 1])

                # 语义分析结束，pop(第i个产生式右部文法符号的个数)
                for i in range(len(right)):
                    sign_stack.pop()
                    status_stack.pop()
                if self.log_level >= 1:
                    print(status_stack, sign_stack, left, right)
                # push(GOTO[新的栈顶状态][第i个产生式的左部])
                status_stack.append(self.analyse_table[status_stack[-1]][left][0])
                sign_stack.append(left)
                if self.log_level >= 1:
                    print(status_stack, sign_stack, left, right)
            # error，退出循环
            if self.tag_list[string_index] not in self.analyse_table[status_stack[-1]].keys():
                return 0
        if self.log_level >= 1:
            pprint(siyuanshi_list)
        with open(self.file_name + '.four', 'w') as f:
            for siyuanshi in siyuanshi_list:
                f.write('%s %s %s %s\n' % (siyuanshi[0], siyuanshi[1],siyuanshi[2],siyuanshi[3],))
        return 1

    def analyse(self, file):
        # 从文件中读取输入串
        try:
            file_name = os.path.basename(file)
            self.file_name = file_name[:file_name.index('.')]
            with open(file, 'r') as f:
                raw_string = f.read()
        except:
            return False
        # 先对输入串进行词法分析
        self.string = raw_string.replace(' ', '').replace('\n', '')
        self.token = ''
        self.index = 0
        self.ch = ''
        self.one_op = ['+', '-', '*', '(', ')', '=', '/']
        self.reserved = []
        self.tag_list = []
        self.string_list = []
        self.two_next = {
            ':': {'=', },
        }
        self.token_to_category = {':=': '='}

        print('analysing: ' + raw_string)
        while self.get_char():
            if self.ch.isalpha():
                case = 'alpha'
            elif self.ch.isdigit():
                case = 'digit'
            elif self.ch in self.one_op:
                case = 'one'
            elif self.ch in self.two_next.keys():
                case = 'two'
            # 不合法字符，报错退出循环
            else:
                print('error index %s: unkown character "%s"' % (self.index, self.ch), end='\n\n')
                return
            # 词法分析出错，报错退出循环
            if not self.switch[case](self):
                print('error index %s: unkown character "%s"' % (self.index, self.token), end='\n\n')
                return
        if self.log_level >= 1:
            print('string', self.string_list)
            print('tag   ', self.tag_list)
        # 将二元式写入文件
        with open(self.file_name + '.two', 'w') as f:
            for string_, tag_ in zip(self.string_list, self.tag_list):
                f.write('%s %s\n' % (string_, tag_))

        # 语法分析
        if self.analyse_lr() == 1:
            print('ok   ', raw_string, end='\n\n')
        else:
            print('fail ', raw_string, end='\n\n')
        return True


start = 'A'
productions = {
    'A': ['V=E', ],
    'E': ['E+T', 'E-T', 'T'],
    'T': ['T*F', 'T/F', 'F'],
    'F': ['(E)', 'i'],
    'V': ['i', ],
}
import os

analyzer = SLRAnalyzer(start, productions, log_level=0)
while True:
    file = input('请输入文件路径：\n')
    if not analyzer.analyse(file):
        break