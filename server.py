from masksystem import *
from socket import *
from threading import *
class server:
    def __init__(self):
        self.DISTRICTS = dict()
        self.all_bookers = []
        self.current_district = ''
        self.port = 12345
        self.ip = 'localhost'
        self.recv_socket = socket(AF_INET,SOCK_DGRAM)
        self.send_socket = socket(AF_INET,SOCK_DGRAM)
        self.send_socket_another = socket(AF_INET,SOCK_DGRAM)
        self.newest_text = ''
        self.text = []

    def send_user(self,id,message,sender=''):
        addr = self.all_bookers[id].addr
        if sender == 'another':
            self.send_socket_another.sendto(message.encode(),addr)
        else:
            self.send_socket.sendto(message.encode(),addr)


    def recv_user(self):
        data, addr = self.recv_socket.recvfrom(1024)
        message = data.decode().split('\n')
        id = int(message[0])
        return id,message[1],addr

    def admin_ins_explain(self,ins):
        if ins.OP == 'append' and len(ins.args)==1:
            if ins.args[0] not in self.DISTRICTS.keys():
                self.DISTRICTS[ins.args[0]] = district(ins.args[0])
            else:
                print('district {} already exist!'.format(ins.args[0]))
        elif ins.OP == 'bookers':
            print('name\tID\tdistrict')
            for b in self.all_bookers:
                if b.online:
                    print('{}\t{}\t{}'.format(b.name,b.ID,b.District))
        elif ins.OP == 'erase' and len(ins.args)==1:
            if ins.args[0] in self.DISTRICTS.keys():
                self.DISTRICTS.pop(ins.args[0])
                if self.current_district == ins.args[0]:
                    self.current_district = ''
                print('erase {} successfully'.format(ins.args[0]))
            else:
                print('district not exist!')
        elif ins.OP == 'districts':
            print('name\tinRound')
            for dk in self.DISTRICTS.keys():
                print('{}\t{}'.format(self.DISTRICTS[dk].Dname,self.DISTRICTS[dk].inRound))
        elif ins.OP == 'enter' and len(ins.args)==1:
            if ins.args[0] in self.DISTRICTS.keys():
                self.current_district = ins.args[0]
            else:
                print("district not exist!")
        elif ins.OP == 'openNewround':
            if self.current_district != '':
                cd = self.current_district
                if self.DISTRICTS[cd].inRound == False:
                    self.DISTRICTS[cd].inRound = True
                    print('open new round successfully.')
                else:
                    print('already in Round!')
            else:
                print('You are not in a district!')
        elif ins.OP == 'list' :
            if self.current_district != '':
                if self.DISTRICTS[self.current_district].inRound ==True:
                    print('the numbers of booker: ',end='')
                    print(self.DISTRICTS[self.current_district].BookerNum)
                    print('the numbers of masks: ',end = '')
                    print(self.DISTRICTS[self.current_district].maskNum)
                    print('booker\tID\tneeds')
                    #通过BOOKERS中存放的ID，引用all_bookers中的booker对象
                    for i in self.DISTRICTS[self.current_district].BOOKERS:
                        print(self.all_bookers[i].name,end='\t')
                        print(self.all_bookers[i].ID,end='\t')
                        print(self.all_bookers[i].needs,end='\n')
                else:
                    print('not in Round')
            else:
                print('You are not in a district!')
        elif ins.OP == 'kickout' and len(ins.args)==1:
            if self.current_district != '':
                cd = self.current_district
                ID = int(ins.args[0])
                if ID in self.DISTRICTS[cd].BOOKERS:
                    self.DISTRICTS[cd].BOOKERS.remove(ID)
                    for id in self.DISTRICTS[cd].BOOKERS:
                        if self.all_bookers[id].online:
                            self.send_user(id,'type:text\n\x00booker:{} has been kicked out'.format(ins.args[0]),'another')
                else:
                    print('no this booker')
            else:
                print('You are not in a district!')
        elif ins.OP == 'handout':
            if self.current_district != '':
                cd = self.current_district
                i = 0            
                for i in range(len(self.DISTRICTS[cd].BOOKERS)):
                    id = self.DISTRICTS[cd].BOOKERS[i]
                    if self.DISTRICTS[cd].maskNum >= self.all_bookers[id].needs:
                        self.DISTRICTS[cd].maskNum -= self.all_bookers[id].needs
                        self.send_user(id,'type:text\n\x00booker:{},You have booked {} masks'.format(id,self.all_bookers[id].needs),'another')
                    else:
                        self.send_user(id,'type:text\n\x00booker:{},sorry, the mask is not enough,You have booked {} masks'.format(id,self.DISTRICTS[cd].maskNum),'another')
                        self.DISTRICTS[cd].maskNum = 0
                self.DISTRICTS[cd].BOOKERS.clear()
                self.DISTRICTS[cd].maskNum = 100000
                self.DISTRICTS[cd].BookerNum = 0
                self.DISTRICTS[cd].inRound = False
        elif ins.OP == 'leave':
            if self.current_district != '':
                self.current_district = ''
                print('leave already.')
            else:
                print('You are not in a district.')
        elif ins.OP == 'msg':
            if len(ins.args) == 2:
                id = int(ins.args[0])
                message = ins.args[1]
                self.send_user(id,'type:text\n\x00'+message,'another')
            elif len(ins.args) == 1:
                for id in range(len(self.all_bookers)):
                    self.send_user(id,'type:text\n\x00'+ins.args[0],'another')
            else:
                print('invalid args.')
        elif ins.OP == 'text':
            if len(ins.args)==1 and ins.args[0] == 'all':
                for m in self.text:
                    print('-------------------------------------------')
                    print (m)
                    print('-------------------------------------------')
            else:
                print(self.newest_text)
        elif ins.OP == 'setMaskNums' and len(ins.args) == 2:
            dName = ins.args[0]
            if dName in self.DISTRICTS.keys() and self.DISTRICTS[dName].inRound == False:
                self.DISTRICTS[dName].maskNum = int(ins.args[1])
            else:
                print('no this district or it is in a round')
        else:
            print('invalid command')
    
    def booker_ins_explain(self,bookerID,ins):
        if bookerID >= 0 and bookerID < len(self.all_bookers) and self.all_bookers[bookerID].online == False:
            return
        if bookerID == -1:
            if ins.OP == 'login' and len(ins.args) == 2:
                bname = ins.args[0]
                new_booker = booker()
                booker_recv_port = int(ins.args[1])
                From_addr =  list(ins.from_addr)
                From_addr[1] = booker_recv_port

                new_booker.addr = tuple(From_addr)
                new_booker.name = bname
                new_booker.ID = len(self.all_bookers)
                new_booker.online = True
                self.all_bookers.append(new_booker)
                self.send_user(new_booker.ID,'ID\n{}'.format(new_booker.ID))
        elif bookerID >= 0 and bookerID < len(self.all_bookers):
            message = ''
            if ins.OP == 'districts':
                message = 'districtName\tinRound\n'
                for name in self.DISTRICTS.keys():
                    message +='{}\t\t{}\n'.format(name,self.DISTRICTS[name].inRound)
                self.send_user(bookerID,'type:reply\x00'+message)
            elif ins.OP == 'list' and len(ins.args)==1:
                dName = ins.args[0]
                if dName in self.DISTRICTS.keys():
                    message = 'the numbers of bookers: {}\n'.format(self.DISTRICTS[dName].BookerNum)
                    message += 'the numbers of masks: {}\n'.format(self.DISTRICTS[dName].maskNum)
                    message += 'booker\tID\tneeds\n'
                    for i in self.DISTRICTS[dName].BOOKERS:
                        message += '{}\t{}\t{}\n'.format(self.all_bookers[i].name,self.all_bookers[i].ID,self.all_bookers[i].needs)
                self.send_user(bookerID,'type:reply\x00'+message)
            elif ins.OP == 'join' and len(ins.args)==1 :
                dName = ins.args[0]
                if dName in self.DISTRICTS.keys():
                    self.DISTRICTS[dName].BOOKERS.append(bookerID)
                    self.all_bookers[bookerID].District = dName
                    self.send_user(bookerID,'type:reply\x00You are in district {}'.format(dName))
                    for i in self.DISTRICTS[dName].BOOKERS:
                        self.send_user(i,message='type:text\n\x00booker:{} join the district{}'.format(bookerID,dName))
                else:
                    self.send_user(bookerID,message='type:reply\x00district not exist!')
            elif ins.OP == 'msg' and len(ins.args)==1 :
                message = ins.args[0]
                message = 'from booker:{}: {}'.format(bookerID,message)
                self.newest_text = message
                self.text.append(self.newest_text)
                for id in range(len(self.all_bookers)):
                    if id != bookerID and self.all_bookers[id].online == True:
                        self.send_user(id,'type:text\n\x00'+message)
                    else:
                        self.send_user(id,'type:reply\x00received.')
            elif ins.OP == 'exit' or ins.OP == 'logout':
                dName = self.all_bookers[bookerID].District
                if dName in self.DISTRICTS.keys():
                    if bookerID in self.DISTRICTS[dName].BOOKERS:
                        self.DISTRICTS[dName].BOOKERS.remove(bookerID)
                self.all_bookers[bookerID].online = False
            elif ins.OP == 'setMaskNeeds' and len(ins.args)==1:
                self.all_bookers[bookerID].needs = int(ins.args[0])
                self.send_user(bookerID,'type:reply\x00set mask number successfully.')

                
    def thread_of_admin(self):
        Ins = ins()
        while True:
            #命令提示
            str_ins = input('Admin@MaskSystem:{}$ '.format(self.current_district)).strip('/')
            #输入指令，若输入成功，则解释指令
            if Ins.Read(str_ins):
                self.admin_ins_explain(Ins)
            else:
                print('invalid command')

    def thread_of_booker(self):
        Ins = ins()
        self.recv_socket.bind(('localhost',12345))
        while True:
            #接收客户端消息
            id,message,addr = self.recv_user()
            #得到该指令的来源地址
            Ins.from_addr = addr
            #将message所代表的指令通过Read转化为ins对象，并解释
            if Ins.Read(message):
                self.booker_ins_explain(id,Ins)
    
    def run(self):
        #处理客户端消息的线程
        booker_thread = Thread(target=self.thread_of_booker,args=())
        booker_thread.setDaemon(True)
        booker_thread.start()
        #与管理员交互的线程
        self.thread_of_admin()


                
Server = server()
Server.run()