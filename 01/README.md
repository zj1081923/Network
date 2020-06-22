## development environment
* ubuntu 16.04
* python 3.6.4

## function
* log_write(f_in_name, f_out_name, mode)
복사할 파일의 이름과 새로운 파일 이름, 그리고 mode를 인자로 넘겨준다. 
mode가 0이면 아래와 같은 형식(복사 시작)을 log에 쓰고,
![1](https://user-images.githubusercontent.com/28529194/85282813-583b6300-b4c7-11ea-9011-19fe69de53a6.JPG)
mode가 1이면 아래와 같은 형식(복사 완료)를 log에 쓴다.
![2](https://user-images.githubusercontent.com/28529194/85282817-5a052680-b4c7-11ea-9760-497b4dd5a2bc.JPG)

* rw_in_1k(f_in_object, f_out_object, size=10000)
10000byte씩 읽고 쓰는 함수이다. f_in_object는 복사할 파일의 object이고 f_out_object는 새로운 파일의 object이다.

* total_process(str_in, str_out)
받아온 input string에 해당하는 파일을 열고 log_write함수를 호출해 로그에 적고 rw_in_1k를 호출해 파일을 복사한다. 그리고 마찬가지로 log_write 함수로 로그에 복사 완료를 쓰고 파일을 닫는다.

## how to test program
소스코드가 있는 디렉토리에 1.77GB부터 41.1KB까지 크기가 다양한 10개의 비디오파일과 이미지파일, 텍스트 파일을 넣었다. 멀티쓰레딩이 잘 동작하는지 확인하기 위해 용량이 큰 순서대로 복사를 수행했다.

![3](https://user-images.githubusercontent.com/28529194/85282818-5a9dbd00-b4c7-11ea-8c8f-56bf5a6db490.JPG)
Input string을 한 파일당 두 개씩 입력 받고, 복사를 완료하기 위해 충분한 시간 후에 “exit”를 입력했다. 정상적으로 종료되는 모습을 확인할 수 있다.

![4](https://user-images.githubusercontent.com/28529194/85282820-5b365380-b4c7-11ea-8440-9d24ee18e31a.JPG)
프로그램을 종료한 후의 디렉토리 모습이다. 각 파일의 복사본과 log파일이 있음을 확인할 수 있다.

![5](https://user-images.githubusercontent.com/28529194/85282826-5c678080-b4c7-11ea-8171-01f408a51839.JPG)
원본 파일과 복사된 파일이 동일함을 확인할 수 있다.

![6](https://user-images.githubusercontent.com/28529194/85282831-5d001700-b4c7-11ea-9b9d-e533dc6f5f0c.JPG)
마지막으로 로그 파일은 다음과 같다. 처음 복사를 시작한 가장 큰 용량의 Tales Runner 191125.mp4의 복사 시간이 오래 걸리지만 해당 파일을 복사하는 동안 다
른 파일들의 복사가 시작되고 또 복사가 완료되었다는 로그들이 기록되어 있다. 따라서 멀티 쓰레딩이 올바르게 구현되었음을 확인했다.
