class booker:
    def __init__(self):
        self.name = ''
        self.ID = -1
        self.needs = 50
        self.addr = ('localhost',54321)
        self.online = False
        self.District = ''

class district:
    DEFAULT_maskNUm = 100000
    def __init__(self,name = ''):
        self.Dname = name
        self.BOOKERS = []
        self.inRound = False
        self.BookerNum = 0
        self.maskNum = district.DEFAULT_maskNUm

class ins:
    admin_op = [
        'msg',
        'bookers',
        'districts',
        'append',
        'enter',
        'erase',
        'openNewround',
        'list',
        'kickout',
        'handout',
        'handout',
        'setMaskNums',
        'leave',
        'text'
    ]
    booker_op = [
        'login',
        'districts',
        'list',
        'join',
        'msg',
        'logout',
        'exit',
        'setMaskNeeds'
    ]
    def __init__(self):
        self.from_addr = ('localhost',54321)
        self.OP = ''    #指令类别
        self.args = []  #参数数组
    def Read(self,str_ins):
        i=0
        j=0
        str_ins = str_ins.strip(' ')
        str_ins = str_ins.strip('/')
        tmp=[]
        while i<len(str_ins):
            if str_ins[i] == ' ':
                tmp.append(str_ins[j:i:])
                while i<len(str_ins) and str_ins[i] == ' ':
                    i+=1
                j=i
            i+=1
        if j<i:
            tmp.append(str_ins[j:i:])
        self.OP = tmp[0]
        self.args = tmp[1:]
        if (self.OP in ins.admin_op or self.OP in ins.booker_op) and len(self.args)<=2:
            return True
        else:
            return False
        
        