## development environment
* window 10
* python 3.7
***
## code explanation
Ass2Server라는 클래스를 만들었다.   
* init_socket   
host socket과 port, ip를 초기화한다.
* run_server   
10080 포트로 클라이언트의 요청을 계속 기다릴 수 있도록 무한 루프 안에서 accept 함수를 호출한다.   
그리고 새로운 thread를 만들어 리턴 값을 보내준다.   
* make_http_header    
http header를 만드는 함수이다.   
요청받은 파일 이름, status code, id, pw, time 값을 인자로 받아 적절한 헤더를 만들어 리턴한다.   
* multi_   
클라이언트의 요청이 들어왔을 때 동작하는 함수이다.   
클라이언트로부터 받은 정보를 parse_data 함수를 이용해 파싱해 필요한 정보를 얻어낸다.   
Id, pw, time 쿠키가 존재하고, 저장된 시간이 현재 시간으로부터 30초 이상 흐른 뒤라면 쿠키를 초기화하고 해당 쿠키가 invalid하다는 것을 validCookie 변수를 통해 명시한다.   
그 후 다음과 같은 흐름으로 요청을 처리한다.   
![1](https://user-images.githubusercontent.com/28529194/85283513-735aa280-b4c8-11ea-9a3f-0886cb0a74aa.JPG)


## program test
* window 10
* chrome
***
서버를 실행시키면 다음과 같은 문구가 프린트된다.   
![2](https://user-images.githubusercontent.com/28529194/85283514-748bcf80-b4c8-11ea-81fe-e523108444ca.JPG)
   
http://localhost:10080/ 으로 접속 시 로그인 창이 나온다.
![3](https://user-images.githubusercontent.com/28529194/85283516-748bcf80-b4c8-11ea-98c4-05f8e2b7f34c.JPG)
   
아이디와 비밀번호를 입력하고 로그인 버튼을 누르면 secret.html 화면으로 넘어간다.
![4](https://user-images.githubusercontent.com/28529194/85283517-75bcfc80-b4c8-11ea-9ef0-f6647bc3173d.JPG)
cookie.html도 로그인 정보가 유효한 동안 남은 시간을 잘 보여준다.
   
![5](https://user-images.githubusercontent.com/28529194/85283506-6fc71b80-b4c8-11ea-94be-d68a4d5fd9fc.JPG)
각각의 파일에 직접 접근해도 이미지 파일을 잘 보여준다.
   
![6](https://user-images.githubusercontent.com/28529194/85283509-72297580-b4c8-11ea-8e6c-33170416f0d6.JPG)
존재하지 않는 파일의 경우, 404 Not Found 화면을 보여준다.
   
![7](https://user-images.githubusercontent.com/28529194/85283510-72c20c00-b4c8-11ea-9b82-26134206b4c3.JPG)
로그인 유효 시간이 지난 후 각 파일에 접근했을 때, 403 Forbidden 화면을 보여준다
