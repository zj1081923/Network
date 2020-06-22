import socket
from threading import *
import pickle


class Client:
    def __init__(self, serverip):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", 10081))
        self.serveraddr = (serverip, 10080)
        self.client_info = {}

        self.inNAT = []

        self.private_ip = self.get_ip()
        self.Exit = False
        self.get_cmd = False

    def get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    def sendAlive(self):
        msg = "keep-alive:"+str(self.id)
        self.sock.sendto(msg.encode(), self.serveraddr)

        timer = Timer(10, self.sendAlive)
        timer.start()
        if self.Exit == True:
            timer.cancel()

    def update_inNAT(self):
        self.inNAT.clear()
        my_publicip = self.client_info[self.id][1]
        my_publicport = self.client_info[self.id][2]
        for id_, addr_ in self.client_info.items():
            if addr_[1] == my_publicip:
                if addr_[2] != 10081 and my_publicport != 10081:
                    self.inNAT.append(id_)



    def recvMsg(self):
        while self.Exit == False:
            info, addr = self.sock.recvfrom(1300)
            info = pickle.loads(info)
            if info[0] == 'show_list':
                self.client_info = info[1]
                for id_, addr_ in self.client_info.items():
                    print(str(id_) + "\t" + str(addr_[1])+":"+str(addr_[2]))
            elif info[0] == 'update':
                self.client_info = info[1]
                self.update_inNAT()
            elif info[0] == 'chat':
                msg = info[1].split(":")
                print("From " + str(msg[0]) +" [" + str(msg[1]) + "]")
            elif info[0] == 'exit':
                print("program will be terminated in a few seconds...")
                break
            self.get_cmd = True

    def Start(self):
        self.id = input("Put your ID: ")

        self.sendAlive()

        recvmsg = Thread(target=self.recvMsg, args=())
        recvmsg.start()

        msg = "reg:"+str(self.id)+":"+str(self.private_ip)
        self.sock.sendto(msg.encode(), self.serveraddr)


        while True:
            if self.get_cmd == True:
                cmd = input()
                cmd = cmd.split(" ", maxsplit=2)
                if cmd[0] == "@show_list":
                    for id_, addr_ in self.client_info.items():
                        print(str(id_) + "\t" + str(addr_[1])+":"+str(addr_[2]))
                elif cmd[0] == "@exit":
                    self.Exit = True
                    msg = "exit:"+str(self.id)
                    self.sock.sendto(msg.encode(), self.serveraddr)
                    self.sock.sendto(pickle.dumps(["exit", self.id]), (self.private_ip, 10081))
                    break
                elif cmd[0] == "@chat":
                    msg = ['chat', str(self.id)+":"+str(cmd[2])]
                    if cmd[1] in self.inNAT:
                        self.sock.sendto(pickle.dumps(msg), (self.client_info[cmd[1]][0], 10081))
                    else:
                        self.sock.sendto(pickle.dumps(msg), (self.client_info[cmd[1]][1], self.client_info[cmd[1]][2]))
                    self.get_cmd = True




if __name__ == '__main__':
    serverip = input("Put server IP: ")
    client = Client(serverip)
    client.Start()
