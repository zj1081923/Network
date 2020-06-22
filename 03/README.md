## development environment
* ubuntu(64-bit), Mininet-VM
* python 3.4.3

## code explanation
* sender.py   
    * def calculate_RTT (sampleRTT, sendinfo)   
    packet의 RTT에 따라서 timeout value를 계산하는 함수이다.     
    Ack를 받을 때마다 아래와 같은 식으로 timeout을 계산하고 값을 업데이트한다.     
    avgRTT와 devRTT의 초기값은 최초의 RTT0이 발생했을 때, 각각 RTT0, 0.5×RTT0로 설정했다. 
        devRTT=0.875×devRTT+0.125×| sampleRTT-avgRTT |
        avgRTT=0.75×avgRTT+0.25×sampleRTT
        timeout=avgRTT+min⁡(60,   4×devRTT)
       
    * def recvAck(log, total_pkt, sendinfo)   
    receiver.py로부터 온 ack를 받아 처리하는 함수이다.   
    정상적인 ack에 대해 timeout value를 계산하기 위해 calculate_RTT 함수를 호출한다.   
    Receiver로부터 받은 ack와 sender에 저장되어 있는 ack인 in_order를 비교해서 normal ack, already received ack, duplicated ack, cumulative ack 네 경우로 나눠서 처리한다.   
    Timeout value 계산을 위한 calculate_RTT 함수는 normal ack에서만 호출했다.    
         Already received ack는 이미 RTT가 계산이 되어 avgRTT에 반영이 된 상태이고, duplicated ack는 같은 수에 대해 여러 번 오기 때문에 적절한 RTT를 계산할 수 없고 cumulative ack의 경우 어떤 packet send에 대한 ack인지 확인할 수 없기 때문이다.   
         따라서 loss probability 등 환경이 바뀌어도 timeout value는 큰 폭으로 바뀌지 않았다.
       
    * def fineSender(sendinfo)   
    ![1](https://user-images.githubusercontent.com/28529194/85284650-83738180-b4ca-11ea-8292-e09e4363383a.JPG)
    데이터를 보내는 함수이다. 처음 시작 시 recvAck thread를 만들어 receiver로부터 ack를 받을 수 있게 하고 meta data를 보낸다.   
    metadata는 dstFilename과 전체 받아야 할 패킷 개수의 정보를 담고 있다. Metadata가 loss될 경우를 대비해 metadata ack를 받았다. 그래서 실제 packet num은 파일 패킷 수보다 1 크다.   
    metadata를 보낸 후로는 file data를 보낸다. 현재의 in_order번째 패킷부터 window size만큼 패킷을 보낸다.   
    in_order packet에 대해 timeout과 3-duplicated ack를 검사하고 retransmit하는데, 이 과정은 in_order이 전체 패킷 개수, 즉 모든 ack를 다 받을 때까지 반복된다.   
    in_order이 모든 ack를 다 받았다면 receiver로 (전체 패킷 개수 + 1)를 보내고 ack를 기다린다. 만약 ack를 받았거나 해당 패킷에 대해 timeout이 발생한다면 sender를 바로 종료한다.
       
       
* receiver.py   
    * def fileReceiver(recvinfo)   
    sender로부터 metadata를 받아 dstFilename과 전체 패킷 개수를 확인한다. in_order 변수에 현재까지 받은 연속된 패킷 중 마지막 packet number를 저장했다.   
    패킷의 seq이 0이면 meta data이므로 dstFilename과 전체 패킷 개수를 저장했다.   
    모든 패킷을 받아 파일에 쓰는 동안 받은 패킷의 seq를 확인하고 expected packet일 때만 in_order를 업데이트해줬다.   
       만약 expected packet이 아니라면 해당 패킷을 버퍼에 넣어주고, 업데이트 되지 않은 in_order를 보내 sender가 duplicated ack를 감지할 수 있도록 했다.   
       Expected packet을 받으면 buffer에 저장되어 있던 모든 packet을 쓰고 buffer를 비워주면서 in_order를 업데이트 해 준다.
       
    * def FIN_signal(recvinfo, in_order, total_pkt, senderip)   
    모든 패킷을 받고 정상적으로 파일을 닫은 다음 호출되는 함수이다.   
    sender로부터 전체 패킷 개수 + 1에 해당하는 패킷을 받을 때까지 전체 패킷 개수 ack를 보내고 종료한다.
   
   
## program test   
`sudo python execute_mn.py 40 Yu_Huiyeol_Sketchbook.mp4 Yu_Huiyeol_Sketchbook_sent.mp4`   
명령어로 실행하면 프로그램이 완료되었을 때 아래와 같은 파일이 생성된다.   
![2](https://user-images.githubusercontent.com/28529194/85284654-840c1800-b4ca-11ea-99ce-f6dd1d52c76a.JPG)
   
   
![3](https://user-images.githubusercontent.com/28529194/85284618-79518300-b4ca-11ea-80ca-3ef011dd8871.JPG)
원본 파일과 새로 생성된 파일이 동일함을 위에서 확인할 수 있다.
   
   
![4](https://user-images.githubusercontent.com/28529194/85284623-7bb3dd00-b4ca-11ea-8ba0-d8b5d24a7fac.JPG)
로그 파일도 정상적으로 쓰여지고 있다.
   
   
## experimentation
실험에 사용한 파일의 크기는 135MB이다. 전송된 파일과 전송 받은 파일은 모두 동일했다.
1. Different probabilities of packet loss
* window size: 40   
* bandwidth: 10Mbps   
* delay: 25ms   
위와 같이 설정하고 packet loss 확률을 2%, 4%, 8%, 16%로 바꿔서 goodput과 average RTT를 계산했다. 각각의 경우마다 10번씩 측정해 평균을 낸 값으로 그래프를 그렸다.   
   
** Goodput Graph **
![5](https://user-images.githubusercontent.com/28529194/85284629-7d7da080-b4ca-11ea-83e4-d6423630d655.JPG)
packet loss 확률이 높아짐에 따라 goodput이 낮아지고 있음을 확인할 수 있다.   
   
** Average RTT Graph **
![6](https://user-images.githubusercontent.com/28529194/85284637-7eaecd80-b4ca-11ea-969a-70a15083957e.JPG)
Packet loss의 확률에 따른 큰 경향성의 변화는 없다. 이는 normal ack에서만 RTT를 계산하기 때문인 것으로 보인다.

2. Different window size
* loss probability: 2%   
* bandwidth: 10Mbps   
* delay: 25ms   
위와 같이 설정하고 window size를 8, 16, 32, 64로 바꿔가며 goodput과 average RTT를 계산했다. 마찬가지로 각각의 경우마다 10번씩 측정해 평균을 낸 값으로 그래프를 그렸다.
   
** Goodput Graph **
![7](https://user-images.githubusercontent.com/28529194/85284641-80789100-b4ca-11ea-86b9-1c840b4b3fe1.JPG)
   
** Average RTT Graph **
![8](https://user-images.githubusercontent.com/28529194/85284647-82425480-b4ca-11ea-8fbc-9181ab7ba255.JPG)
   
