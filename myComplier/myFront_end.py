from myComplier import myCompiler
from tkinter import *
from tkinter import ttk
import sys
import tkinter.filedialog


class FrontEnd:

    def __init__(self):
        self.temp_file = 'temp.txt'
        self.log_level = 0
        self.in_file = 'input.txt'

        self.root = Tk()
        self.root.title('a simple compiler')
        # self.root.state("zoomed")

        self.label = Label(self.root, text=self.in_file, wraplength=300, justify='left')
        self.label.grid(row=0, column=0, columnspan=3)
        self.botton_file = Button(self.root, text="选择文件", command=self.select_file)
        self.botton_file.grid(row=0, column=3, sticky=W + E + N + S)

        self.boxlist_value = tkinter.StringVar()  # 窗体自带的文本，新建一个值
        self.boxlist = ttk.Combobox(self.root, textvariable=self.boxlist_value)  # 初始化
        self.boxlist["values"] = ("0", "1", "2")
        self.boxlist.current(0)  # 选择第一个
        self.boxlist.grid(row=1, column=0, columnspan=3, sticky=W + E + N + S)
        self.botton_log = Button(self.root, text="设置log等级", command=self.set_log_level)
        self.botton_log.grid(row=1, column=3, sticky=W + E + N + S)

        self.out_text = Text(self.root)
        self.out_text.grid(row=2, column=0, sticky=W + E + N + S, columnspan=4)
        self.scrol = Scrollbar(self.out_text)
        self.scrol.config(command=self.out_text.yview)
        self.out_text.config(yscrollcommand=self.scrol.set)

        self.button_analyse = Button(self.root, text='分析', command=self.analyse)
        self.button_analyse.grid(row=3, column=0, sticky=W + E + N + S, columnspan=4)

        self.root.mainloop()

    def analyse(self):
        console = sys.stdout
        with open(self.temp_file, 'w') as temp_file:
            sys.stdout = temp_file
            self.compiler = myCompiler.Compiler(log_level=self.log_level)
            self.compiler.analyse(self.in_file)
        sys.__stdout__ = console
        with open(self.temp_file, 'r') as f:
            self.out_text.insert(END, f.read())
            self.out_text.see(END)

    def select_file(self):
        self.in_file = tkinter.filedialog.askopenfilename()
        if self.in_file != '':
            self.label.config(text=self.in_file)
        else:
            self.label.config(text="您没有选择任何文件")

    def set_log_level(self):
        self.log_level = int(self.boxlist.get())

front_end = FrontEnd()


