import socket
from threading import *
import time
import pickle



class Server:
    def __init__(self):
        self.client_info = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", 10080))
        self.client_alive = {}


    def checkAlive(self):
        while True:
            try:
                for id, T in self.client_alive.items():
                    if time.time()-T > 30:
                        print(str(id) + " is off-line\t" + str(self.client_info[id][1])+":"+str(self.client_info[id][2]))
                        self.client_alive.pop(id)
                        self.client_info.pop(id)
                        self.update_info()
                        break
            except Exception:
                continue

    def showList(self, addr):
        data = ["show_list", self.client_info]
        self.sock.sendto(pickle.dumps(data), (addr[0], addr[1]))

    def update_info(self):
        data = ["update", self.client_info]
        for id_, addr_ in self.client_info.items():

            self.sock.sendto(pickle.dumps(data), (addr_[1], addr_[2]))


    def recvCmd(self):

        checkalive = Thread(target=self.checkAlive, args=())
        checkalive.start()

        while True:
            msg, addr = self.sock.recvfrom(300)
            msg = str(msg.decode())
            msg = msg.split(":")

            if msg[0] == 'keep-alive':
                self.client_alive[msg[1]] = time.time()
            elif msg[0] == 'reg':
                self.client_info[msg[1]] = [msg[2], addr[0], addr[1]]
                print(str(msg[1]) + "\t" + str(addr[0]) + ":" + str(addr[1]))
                self.update_info()
                self.showList(addr)
            elif msg[0] == 'show_list':
                self.showList(addr)
            elif msg[0] == 'exit':
                print(str(msg[1])+" is unregistered\t" + str(self.client_info[msg[1]][1])+":"+str(self.client_info[msg[1]][2]))
                self.client_info.pop(msg[1])
                self.client_alive.pop(msg[1])
                self.update_info()




if __name__ == '__main__':
    server = Server()
    server.recvCmd()