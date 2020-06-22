## development environment
* window 10
* python 3.7
   
## code explanation
* server.py
     **변수**   
     `client_info`: 딕셔너리이며, key는 client id, value는 해당 client의 private ip, public ip, public port number로 구성된 리스트이다.   
     `client_alive`: 리스트이며 client의 id와 keep-alive 메시지를 받은 시간으로 구성되어 있다.   

     **def checkAlive()**   
     별도의 쓰레드를 생성해 checkAlive() 함수를 실행한다. client들은 10초에 한 번씩 keep-alive 메시지를 서버로 보내는데, 받은 keep-alive의 시간을 recvCmd() 함수에서 client_alive 딕셔너리를 이용해 업데이트 해 준다. checkAlive() 함수는 이렇게 업데이트 된 client_alive의 정보를 순회하며 keep-alive 메시지를 받은 지 30초가 넘은 client 정보들을 제거하며, off line이 되었음을 알린다. 그리고 해당 client 정보를 삭제한 client_info를 update_info() 함수를 호출함으로써 연결되어 있는 모든 client들에게 업데이트 된 client_info를 전송하도록 한다.   

     **def showList(addr)**   
     @show_list 명령을 내린 client에게 client_info 정보를 전송하는 함수이다.   

     **def update_info()**  
     client 정보가 업데이트(register, offline, exit) 되었을 경우에 호출하는 함수이다. client_info에 저장되어 있는 모든 client들에게 업데이트 된 client_info 정보를 전송한다.   

     **def recvCmd()**   
     client로부터 메시지를 받아 처리하는 역할을 하는 함수이다. 일단 client로부터 어떠한 메시지를 받으면 아래와 같이 나누고 처리한다.   
     1. keep-alive  
         client가 10초에 한 번씩 주기적으로 보내는 메시지이다. 받은 시간을 client_alive 딕셔너리에 업데이트한다.   
     2. register   
         새로운 client를 등록한다. client_info에 private ip, public ip, public port number를 업데이트한다. client_info가 업데이트 되었으므로 update_info() 함수를 호출하고, client에서는 바로 현재 등록된 client의 정보를 띄워야 하므로 show_list(addr) 함수를 호출한다.   
     3. show_list  
         show_list(addr) 함수를 호출한다.  
     4. exit  
         client가 종료되었으므로, client_info에서 해당 client의 정보를 삭제하고 client_alive에서도 해당 정보를 삭제한다. 또한 client_info의 정보가 업데이트 되었으므로 update_info() 함수 호출을 통해 연결된 모든 client에게 업데이트 된 정보를 전송한다.   

* client.py
    **변수**   
    `client_info`: 딕셔너리이며, server에 있는 client_info와 동일한 정보를 저장한다.   
    `inNAT`: 같은 NAT 안에 있는 client들의 id를 저장하는 리스트이다.   
       
    **def get_ip()**   
    자기 자신의 private ip를 얻는 함수이다.   
       
    **def sendAlive()**   
    10초에 한 번씩 server로 keep-alive 메시지를 전송한다. 만약 Start() 함수에서 사용자에게 @exit를 입력받았다면 Start에서 Exit 변수를 True로 변경하는데, 만약 sendAlive()함수에서 `Exit==True`임을 인지한다면 10초로 설정된 타이머를 캔슬하고 쓰레드를 종료한다.
       
    **def update_inNAT()**   
    같은 NAT 안에 있는 client들의 정보를 업데이트하는 함수이다. 만약 public ip가 같은데, public port가 10081이 아니라면 같은 NAT를 통해 translation된 것으로 판단하고 inNAT 리스트에 해당 client id를 추가한다.   
       
    **def recvMsg()**   
    server, 혹은 다른 client나 자기 자신에게 오는 모든 메시지를 받아 처리하는 함수이다. 메시지의 내용은 아래와 같다.   
        1. show_list: 서버로부터 받은 메시지이다. client_info를 업데이트하고 해당 정보를 사용자에게 보여준다.   
        2. update: 서버로부터 받은 client_info 업데이트 메시지이다. client_info에 변화가 생겼으므로 서버로부터 받은 정보로 업데이트해준다.   
        3. chat: 다른 client로부터 받은 채팅 메시지이다. 보낸 client id와 메시지를 사용자에게 보여준다.   
        4. exit: 사용자가 @exit 명령을 통해 client를 종료했다는 메시지이다. 별도의 쓰레드로 돌고 있으므로 자기 자신에게 exit 메시지를 보내 recvMsg()를 종료시킨다.   
       
    **def Start()**   
    사용자로부터 명령어를 입력 받아 처리하는 함수이다. 처음에는 사용자로부터 client id를 입력 받고 바로 server로 register 메시지를 보낸다. 그 후로 @exit, 혹은 keyboard interrupt 전까지 계속 명령어를 입력 받는다. 입력 받는 명령어에 따른 처리는 아래와 같다.   
        1. `@show_list`: 해당 명령어를 받으면 현재 저장되어 있는 client_info 정보를 통해 모든 client id, public ip address, public port number를 보여준다.   
        2. `@exit`: Exit 변수를 True로 설정해 sendAlive()가 종료될 수 있도록 한다. 그리고 recvMsg() 쓰레드를 종료시키기 위해 자기 자신에게 exit 메시지를 전송하고, while문을 빠져나와 Start() 함수가 종료될 수 있도록 한다.   
        3. `@chat`: 상대 client에게 보낼 메시지를 설정하고, 만약 보내려는 client id가 inNAT 리스트에 존재한다면 같은 NAT 안에 있으므로 (private ip, 10081)로 해당 메시지를 전송하고, 그 외의 경우에는 현재 NAT 밖에 있는 client이므로 (public ip, public port number)로 메시지를 전송한다.   
        
   
