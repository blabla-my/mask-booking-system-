from socket import *
from masksystem import *
from threading import *
from time import sleep,time
from random import randint

SERVER_PORT = 12345
recv_port = randint(10000,50000)

des_addr = ('localhost',SERVER_PORT)
local_addr = ('localhost',recv_port)

class client:
    def __init__(self):
        self.ID = -1
        self.name = 'panda'
        self.District = ''
        self.send_socket = socket(AF_INET,SOCK_DGRAM)
        #self.ins_recv_socket = socket(AF_INET,SOCK_DGRAM)
        self.recv_socket = socket(AF_INET,SOCK_DGRAM)
        self.newest_text = ''
        self.history_text = []
        self.last_reply_got = True
        self.needs = 50
        self.recv_socket.bind(local_addr)

    def clear(self):
        self.ID = -1
        self.name = 'unknown'
        self.District = ''
        self.newest_text = ''
        self.history_text = []
        self.last_reply_got = True
        self.needs = 50

    def send_server(self,message):
        mes = '{}\n{}'.format(self.ID,message)
        self.send_socket.sendto(mes.encode(),des_addr)

    '''def ins_recv_server(self):
        message,addr = self.ins_recv_socket.recvfrom(1024)
        print("recv:",message)
        return message'''

    def recv_server(self):
        message,addr = self.recv_socket.recvfrom(1024)
        message = message.decode()
        return message

    def login(self):
        Ins = ins()
        while True:
            login_ins = input('please login with command "/login UserName":\n')
            if Ins.Read(login_ins) and Ins.OP == 'login':
                self.name = Ins.args[0]
                self.send_server(login_ins+' '+str(recv_port))
                break
            elif Ins.OP == 'exit':
                exit(0)

    def thread_interactive_send(self):
        Ins = ins()
        self.login()
        while True:
            str_ins = input('{}@maskclient:{}$ '.format(self.name,self.District))
            if Ins.Read(str_ins):
                self.send_server(str_ins)
                if Ins.OP == 'exit':
                    exit()
                elif Ins.OP == 'logout':
                    self.clear()
                    self.login()
                else:
                    self.last_reply_got = False
                    start_wait_time = time()
                    #循环等待3s
                    while self.last_reply_got != True and time()-start_wait_time<=3:
                        pass
                    #若3s内无回应
                    if self.last_reply_got == False:
                        print('server no reply.')
            else:
                if Ins.OP == 'text':
                    if len(Ins.args) == 1 and Ins.args[0] == 'all':
                        for m in self.history_text:
                            print('-------------------------------------------')
                            print (m)
                            print('-------------------------------------------')
                    else:
                        print(self.newest_text)
                else:
                    print('invalid command.')
    
    def thread_interactive_recv(self):

        while True:     #waiting for ID
            message = self.recv_server()
            if 'ID\n' in message:
                self.ID = int(message.split('\n')[1])
                break
        while True:
            message = self.recv_server()
            if 'type:text\n\x00' in message:
                self.newest_text = message
                self.history_text.append(message)
            elif 'type:reply\x00' in message:           #if message is the reply of client's command, print the reply
                if 'in district ' in message:
                    self.District = message.split('in district ')[1] 
                self.last_reply_got = True
                print(message.strip('type:reply\x00'))
    
    def run(self):
        #接收消息线程
        recv_thread = Thread(target=self.thread_interactive_recv,args=())
        recv_thread.setDaemon(True)
        recv_thread.start()       
        #发送消息线程
        self.thread_interactive_send()

Client = client()
Client.run()