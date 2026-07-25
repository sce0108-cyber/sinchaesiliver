# Python Port Scanner

네트워크 기초 4주차 과제 — `socket` 모듈로 만든 TCP 포트 스캐너입니다.

> ⚠️ 본인 소유이거나 스캔이 허가된 호스트(127.0.0.1, 직접 띄운 서버, scanme.nmap.org)에만 사용하세요.

## 파일 구성

| 파일 | 설명 |
|---|---|
| `scanner1.py` | Level 1. 대화형 입력(input) 받아서 순차적으로 스캔 |
| `scanner.py` | Level 2. argparse + 멀티스레드 + 서비스 이름 추정 |

## 실행 방법

```bash
# Level 1 (대화형 입력)
python3 scanner1.py

# Level 2
python3 scanner.py --host 127.0.0.1 --ports 1-1000
python3 scanner.py --host 127.0.0.1 --ports 22,80,443 --threads 100
python3 scanner.py --host 127.0.0.1 --ports 1-1000 --benchmark
```

### 옵션

| 옵션 | 기본값 | 설명 |
|---|---|---|
| `--host` | (필수) | 대상 IP 또는 도메인 |
| `--ports` | 1-1024 | `1-1000`, `22,80,443`, `1-100,8080` 형식 지원 |
| `--threads` | 50 | 동시 스레드 개수 |
| `--timeout` | 1.0 | 포트당 응답 대기 시간(초) |
| `--show-closed` | off | 닫힌 포트도 출력 |
| `--benchmark` | off | 순차 vs 스레드 소요 시간 비교 |

## 실행 결과

### Level 1 (scanner1.py)

3000번에 개발 서버 띄워둔 상태에서 그 주변 포트만 잡아서 돌림.

```
$ python3 scanner1.py
Target IP/domain (예: 127.0.0.1): 127.0.0.1
Port range (예: 1-100): 2990-3010

Target: 127.0.0.1 (127.0.0.1)
Scanning ports 2990-3010...

Port 2990: CLOSED
Port 2991: CLOSED
Port 2992: CLOSED
Port 2993: CLOSED
Port 2994: CLOSED
Port 2995: CLOSED
Port 2996: CLOSED
Port 2997: CLOSED
Port 2998: CLOSED
Port 2999: CLOSED
Port 3000: OPEN
Port 3001: CLOSED
Port 3002: CLOSED
Port 3003: CLOSED
Port 3004: CLOSED
Port 3005: CLOSED
Port 3006: CLOSED
Port 3007: CLOSED
Port 3008: CLOSED
Port 3009: CLOSED
Port 3010: CLOSED

Scan complete in 0.00s. 1 open port(s) found out of 21.
```

### Level 2 (scanner.py)

127.0.0.1로 돌리면 열린 포트가 거의 없어서 재미가 없길래, README에 이미 적어둔 대로 스캔이 허가된 scanme.nmap.org로도 테스트.

```
$ python3 scanner.py --host scanme.nmap.org --ports 1-200 --timeout 1
Scanning scanme.nmap.org (45.33.32.156) (ports 1-200) with 50 threads...

Port    22 (ssh): OPEN
Port    80 (http): OPEN

Scan finished in 1.45s (open: 2, closed: 198)
```

로컬(127.0.0.1)에서는 이렇게 나옴. 내가 띄워둔 개발 서버(3000번)만 OPEN으로 잡힘.

```
$ python3 scanner.py --host 127.0.0.1 --ports 22,80,443,3000,3306,5432,8080 --show-closed
Scanning 127.0.0.1 (127.0.0.1) (ports 22,80,443,3000,3306,5432,8080) with 50 threads...

Port  3000 (node/dev-server): OPEN
Port    22 (ssh): CLOSED
Port    80 (http): CLOSED
Port   443 (https): CLOSED
Port  3306 (mysql): CLOSED
Port  5432 (postgresql): CLOSED
Port  8080 (http-proxy): CLOSED

Scan finished in 0.00s (open: 1, closed: 6)
```

## 구현 과정

1. **Level 1 (scanner1.py) 먼저 작성** — `socket.socket(AF_INET, SOCK_STREAM)`으로 TCP 소켓을 만들고, `settimeout()`으로 타임아웃을 건 다음 `connect_ex()`의 반환값이 0인지로 open/closed를 판별. 입력은 `input()`으로 대상 IP/도메인과 포트 범위를 받도록 함.
2. **포트 범위 파싱** — `"1-1000"` 같은 문자열을 정수 리스트(또는 범위)로 변환하는 부분을 scanner.py 쪽에서는 `,`와 `-`를 둘 다 지원하도록 확장(`parse_ports`).
3. **Level 2 (scanner.py)로 확장** — 순차 스캔 함수(`scan_sequential`)는 그대로 두고, `ThreadPoolExecutor`를 쓰는 `scan_threaded`를 추가해서 같은 포트 리스트를 동시에 검사하도록 함.
4. **서비스 이름 매핑** — 자주 쓰는 포트는 `COMMON_SERVICES` 딕셔너리로 직접 정의하고, 거기 없는 포트는 `socket.getservbyport()`로 조회하되 없으면 `unknown`으로 처리(`guess_service`).
5. **argparse 적용** — `--host`, `--ports`, `--threads`, `--timeout`, `--show-closed`, `--benchmark` 옵션을 추가해서 CLI로 실행 가능하게 함.
6. **벤치마크 기능 추가** — `--benchmark` 옵션으로 같은 포트 목록에 대해 순차/스레드 스캔을 각각 돌리고 `time.perf_counter()`로 소요 시간을 비교하도록 함.

### 삽질 기록

ai한테 터미널에 입력할 값들을 물어보고 직접 실행해봤는데 ai가 준 스크립트가 제대로 작동하지 않아서 지속적으로 스크립트를 수정해가며 공부하였다.
$ python3 scanner.py --host scanme.nmap.org --ports 1-200 --timeout 1
$ python3 scanner1.py
$ python3 scanner.py --host 127.0.0.1 --ports 22,80,443,3000,3306,5432,8080 --show-closed

## 속도 측정 결과

`--benchmark` 옵션으로 측정함. 과제에서 하라는 대로 127.0.0.1 1-1000 포트로 먼저 재봤는데, 순차나 스레드나 거의 차이가 없었음. 그래서 filtered 포트가 섞여있는 scanme.nmap.org로도 한 번 더 재봄.

| 방식 | 대상 | 포트 수 | 소요 시간 |
|---|---|---|---|
| 순차 | 127.0.0.1 | 1-1000 | 0.03s |
| 스레드 50개 | 127.0.0.1 | 1-1000 | 0.04s |
| 순차 | scanme.nmap.org | 1-200 | 32.25s |
| 스레드 50개 | scanme.nmap.org | 1-200 | 1.42s |

측정 환경: macOS (Darwin 25.4.0) / Python 3.14.4 / timeout 1.0s

**분석:** 

127.0.0.1에서는 순차와 스레드 속도 차이가 거의 없었음. 닫힌 포트라도 로컬에서는 RST 응답이 즉시 오기 때문에 애초에 기다릴 게 없어서 스레드로 동시에 돌리는 이점이 안 나타난 것. 반면 scanme.nmap.org는 방화벽에 막힌 포트가 섞여있어서 순차 스캔은 그런 포트마다 timeout을 꽉 채워 기다려야 했고 그게 200번 누적되니 32초가 걸림. 스레드로 돌리면 그 대기 시간들이 겹쳐서 진행되기 때문에 1.42초로 끝남. 결국 스레드의 이득은 응답이 느리거나 없는 대상을 스캔할 때 확실히 드러남.

## 체크포인트 질문

### 1. 포트 하나를 확인할 때 3-Way Handshake는 어느 단계까지 일어나는가?



- 열린 포트일 때: SYN → SYN/ACK → ACK 까지 3단계가 다 일어남. connect_ex()가 0을 반환하는 시점이 ACK까지 보낸 뒤임.
- 닫힌 포트일 때: 상대가 SYN을 받자마자 RST로 바로 거절해서 handshake가 1단계(SYN)만 가고 끝남. ACK 단계까지 못 감.
- 방화벽이 막았을 때: SYN을 보내도 응답 자체가 안 옴. handshake가 아예 시작도 못 하고, 코드에서는 그냥 timeout 시간만큼 기다리다가 실패로 처리됨.

### 2. `connect_ex`와 `connect`의 차이는? 왜 스캐너에는 `connect_ex`가 적합한가?


`connect()`는 연결에 실패하면 예외를 던져서 포트마다 try/except로 감싸야 함. 반면 `connect_ex()`는 예외 대신 결과를 정수로 반환 — 성공하면 0, 실패하면 errno 값. 포트 스캐너는 수백~수천 개 포트를 반복문으로 돌려야 하는데 그때마다 예외 처리를 하는 것보다 반환값만 비교하는 게 코드도 간단하고 오버헤드도 적어서 `connect_ex`가 더 적합함.

### 3. 스레드를 너무 많이 띄우면 어떤 문제가 생기는가?


- 스레드마다 스택 메모리를 OS가 할당하기 때문에 수천 개씩 띄우면 메모리 사용량이 커짐.
- 소켓도 스레드 수만큼 동시에 열리는데 OS가 프로세스당 열 수 있는 파일 디스크립터 개수를 제한해놔서 Too many open files 같은 에러가 날 수 있음.
- 스레드가 너무 많아지면 컨텍스트 스위칭 비용이 늘어나서 어느 지점부터는 스레드를 늘려도 성능이 오히려 정체되거나 떨어짐.
- 짧은 시간에 연결 시도가 몰리기 때문에 대상 서버의 방화벽이나 IDS가 이상 트래픽으로 탐지하고 차단할 수도 있음.

## 참고 자료

- Python 공식 문서 — `socket`, `concurrent.futures`, `argparse`
- Nmap 공식 문서 — Port Scanning Techniques

##추가적으로 공부할 것
파이썬 socket
네트워크 구조 기초
nmap 