import socket
from _thread import *
import os
import mimetypes
import time





PORT = 10080
#HOST_IP = "192.168.0.32"
HOST_IP = ""




class UserInfo:
    def __init__(self, id, pw, time_):
        self.id = id
        self.pw = pw
        self.time_ = time_

class Ass2Server:
    def __init__(self, port, host_addr):
        self.host_socket = None
        self.host_port = port
        self.host_ip = host_addr
        self.userid = []

    def init_socket(self):
        self.host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.host_socket.bind((self.host_ip, self.host_port))
        self.host_socket.listen() #클라이언트의 접속 허용
        print("server is ready...")

    def run_server(self):
        print("server is running...")
        while True:
            #print("wait....")
            self.client_socket, addr = self.host_socket.accept()
            start_new_thread(self.multi_, (self.client_socket, addr))

    def parse_data(self, datastr):
        #print("<client request>")
        #print(datastr)
        isCookie = False
        # 요청받은 주소 이름
        try:
            html_name = datastr.split(" ", 2)[1]
        except IndexError:
            print("no client message...")
            html_name = None
        # get version
        '''if html_name.startswith('/secret.html?id='):
                    #print("@@")
                    cookie_info = html_name.replace("&", "=").split("=")
                    html_name = html_name.split("?")[0]
                    #print(cookie_info)
                    id = cookie_info[1]
                    pw = cookie_info[3]
                    time_ = str(int(time.time()))
                    isCookie = True'''

        # post version
        if datastr.split(" ",2)[0] == "POST":
            #print("post version")
            input_info = datastr.split("\r\n\r\n")[1]
            input_info = input_info.replace("&", "=").split("=")
            id = input_info[1]
            pw = input_info[3]
            time_ = int(time.time())
            isCookie = True
            ### 헤라가 말한 부분 구현 ###
            '''tmp_user = None
            for user in self.userid:
                if user.id == id : # 있지만 만료되었을 경우..
                    tmp_user = user
                    if int(time.time() - int(user.time_)) > 30:
                        id = ""
                        pw = ""
                        time_ = ""
                        isCookie = False
                    break
            if isCookie == True:
                self.userid.append(UserInfo(id, pw, time_))
                if tmp_user != None:
                    self.userid.remove(tmp_user)'''
            #############################


        # cookie (id, pw, time)
        else:
            #print("##")
            header_info = datastr.split("\r\n")
            cookie_info = None
            for info in header_info:
                if info.startswith('Cookie: '):
                    cookie_info = info
                    break
            if cookie_info == None:
                id = ""
                pw = ""
                time_ = ""
            else:
                cookie_info = cookie_info.replace("=", ";").split(";")
                if len(cookie_info) < 6:
                    id = ""
                    pw = ""
                    time_ = ""
                else:
                    id = cookie_info[1]
                    pw = cookie_info[3]
                    time_ = cookie_info[5]
                if id != '' and pw != '' and time_ != '':
                    isCookie = True
        return html_name, id, pw, time_, isCookie




    def make_http_header(self, name, status_code, id, pw, time):
        if status_code == 200:
            length = os.stat(name).st_size
            type, encode = mimetypes.guess_type(name)
            strStatus = "200 OK"
        elif status_code == 403:
            strStatus = "403 Forbidden"
            type = "text/plain"
            length = len("403 Forbidden")
        elif status_code ==404:
            strStatus = "404 Not Found"
            type = "text/plain"
            length = len("404 Not Found")
        else:
            type = "application/octet-stream"
        http_header = "HTTP/1.1: "+strStatus+"\r\nContent-Length: "+str(length)+"\r\nContent-Type: "+type+"\r\nSet-Cookie: id="+id+"\r\nSet-Cookie: pw="+pw+"\r\nSet-Cookie: time="+str(time)+"\r\nKeep-Alive: timeout=100, max=100\r\nConnection: Keep-Alive\r\n\r\n"
        return http_header

    def load_file(self, filename):
        try:
            file = open(filename, "rb")
            return file, 200
        except FileNotFoundError:
            return "404 Not Found".encode(), 404


    def multi_(self, client_socket, addr):

        while True:
            data = client_socket.recv(2048).decode()
            req_name, userid, userpw, usertime, validCookie = self.parse_data(data)
            if req_name == None:
                break
            #print(req_name)
            #print(userid)
            #print(userpw)
            #print(usertime)
            #print(str(validCookie))

            if validCookie == True: #30초지나면 Cookie는 만료
                if int(time.time())-int(usertime) > 30:
                    validCookie = False
                    userid = ""
                    userpw = ""
                    usertime = ""

            if req_name == "/" or req_name == "/index.html":
                if validCookie == True:
                    req_name = "/secret.html"
                elif validCookie == False:
                    req_name = "/index.html"
            req_name = req_name.replace("/", "")

            if req_name == "cookie.html":
                if validCookie == True:
                    remain_time = 30 - (int(time.time()) - int(usertime))
                    html_str = "<!DOCTYPE html><html><head><title>Welcome to " + userid + "</title></head><body><p>Hello " + userid + "</p><p>" + str(
                        remain_time) + " seconds left until your cookie expires.</p></body></html>"
                    header = "HTTP/1.1: "+"200 OK"+"\r\nContent-Length: "+str(len(html_str))+"\r\nContent-Type: "+"text/html"+"\r\nSet-Cookie: id="+userid+"\r\nSet-Cookie: pw="+userpw+"\r\nSet-Cookie: time="+str(usertime)+"\r\n\r\n"


                    client_socket.send(header.encode())
                    client_socket.send(html_str.encode())
                    #client_socket.send(file.read())

                elif validCookie == False:
                    header = self.make_http_header(None, 403, userid, userpw, usertime)
                    client_socket.send(header.encode())
                    client_socket.send("403 Forbidden".encode())

            elif req_name == "index.html" or req_name == "favicon.ico":
                file, status_code = self.load_file(req_name)
                header = self.make_http_header(req_name, status_code, userid, userpw, usertime)
                client_socket.send(header.encode())
                client_socket.send(file.read())

            #elif req_name != "index.html":
            else:
                if validCookie == True:
                    file, status_code = self.load_file(req_name)
                    header = self.make_http_header(req_name, status_code, userid, userpw, usertime)
                    client_socket.send(header.encode())
                    if status_code == 404:
                        client_socket.send("404 Not Found".encode())
                    else:
                        client_socket.send(file.read())

                elif validCookie == False:
                    header = self.make_http_header(None, 403, userid, userpw, usertime)
                    client_socket.send(header.encode())
                    client_socket.send("403 Forbidden".encode())

            #print("<server response>")
            #print(header)

            break
        client_socket.close()



if __name__ == "__main__":
    server = Ass2Server(PORT, HOST_IP)
    server.init_socket()
    server.run_server()