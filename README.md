# 📚 sinchaesilver — 학습 기록 저장소

C 언어 기초부터 시스템 해킹(포너블), 웹 보안, 네트워크 프로그래밍, 웹 풀스택 개발, 그리고 AI 연동 캡스톤 프로젝트까지 — 직접 작성하고 정리한 학습/실습 코드 모음입니다.

> 폴더별 상세 설명과 실행 방법은 각 폴더 안의 `README.md`에 더 자세히 있습니다.

---

## 🗂 폴더별 요약

| 폴더 | 분야 | 한 줄 요약 |
|---|---|---|
| [`코드업`](./코드업) | C 기초 문법 | 출력/조건문/반복문/연산자 등 C 기초 알고리즘 문제 풀이 |
| [`BufferOverflow_prac`](./BufferOverflow_prac) | 시스템 해킹 (Pwnable) | 스택 버퍼 오버플로우 실습 — 메모리 구조·리턴 주소 변조 이해 |
| [`Xss_wargame_Prac`](./Xss_wargame_Prac) | 웹 보안 | 직접 만든 XSS 취약점 실습용 Flask 워게임 서버 |
| [`dreamhack_prac`](./dreamhack_prac) | 웹 보안 | 드림핵(Dreamhack) XSS·CSRF 워게임 문제 풀이 + Write-up |
| [`PythonPortScanner`](./PythonPortScanner) | 네트워크 프로그래밍 | Python `socket` 기반 TCP 포트 스캐너 (멀티스레드) |
| [`MovieChartWeb_prac`](./MovieChartWeb_prac) | 웹 풀스택 개발 | Node.js/Express + TMDB API로 만든 영화 차트 웹앱 |
| [`캡디2`](./캡디2) | 캡스톤 디자인 (팀 프로젝트) | SimPy 기반 멀티로봇 공장 시뮬레이터 + AI 관제 콘솔 |

---

## 🔎 폴더별 상세

### [`코드업`](./코드업) — C 언어 기초
Codeup 사이트의 기초 문제들을 C로 풀이한 코드 모음입니다. `printf`/`scanf`, 조건문, 반복문, 배열 등 C 문법의 기본기를 다졌습니다.

### [`BufferOverflow_prac`](./BufferOverflow_prac) — 시스템 해킹 입문
`-fno-stack-protector -no-pie` 옵션으로 보호 기법을 의도적으로 끈 바이너리(`rao.c`)를 대상으로 스택 버퍼 오버플로우를 실습했습니다. 스택 프레임 구조, 리턴 주소 덮어쓰기, 쉘 획득(`execve`) 흐름을 이해하는 데 초점을 맞췄습니다. (교육 목적, 로컬 환경 전용)

### [`Xss_wargame_Prac`](./Xss_wargame_Prac) — XSS 원리를 직접 만들며 학습
Flask로 **일부러 취약하게** 만든 워게임 서버를 직접 설계·구현했습니다.
- Level 1: Reflected XSS (필터 없음)
- Level 2: Stored XSS (방명록에 저장되는 구조)
- Level 3~4: 블랙리스트 필터 우회 (태그 제거, 키워드 중첩 우회 등)

공격 코드를 가져다 쓰는 대신, **취약점이 발생하는 서버 쪽 로직 자체를 구현**해보면서 원리를 학습했습니다.

### [`dreamhack_prac`](./dreamhack_prac) — 웹 해킹 워게임 Write-up
드림핵의 XSS·CSRF 문제를 실제로 풀이하고 과정을 Write-up으로 정리했습니다.
- CSRF: 로그인 세션 탈취 없이도, 토큰 검증이 없는 비밀번호 변경 API를 이용해 관리자 비밀번호를 변조하는 공격 시나리오 분석
- XSS: 헤드리스 브라우저(Selenium) 기반 관리자 봇을 대상으로, 같은 오리진의 다른 페이지(`/memo`)를 저장소처럼 활용하는 우회 트릭 등 시행착오 과정을 기록

### [`PythonPortScanner`](./PythonPortScanner) — 네트워크 프로그래밍
Python `socket` 모듈로 TCP 포트 스캐너를 단계적으로 발전시켰습니다.
- Level 1: `connect_ex` 기반 순차 스캔 (대화형 입력)
- Level 2: `argparse` + `ThreadPoolExecutor` 멀티스레드 + 서비스 이름 추정 + 벤치마크 기능

순차 스캔과 스레드 스캔의 속도 차이를 직접 측정하고, 3-Way Handshake·`connect`/`connect_ex` 차이 같은 네트워크 기초 개념도 README에 정리했습니다.

### [`MovieChartWeb_prac`](./MovieChartWeb_prac) — 웹 풀스택 개발
Node.js + Express 서버에서 TMDB(The Movie DB) Open API를 호출해 인기 영화 목록을 보여주는 웹앱입니다. 서버 라우팅, 외부 API 연동, `.env`를 이용한 API 키 관리, EJS 템플릿 렌더링을 실습했습니다.

### [`캡디2`](./캡디2) — 캡스톤 디자인 2 (팀 프로젝트)
IC-PBL 캡스톤 디자인 과목에서 진행한 **멀티로봇 공장 시뮬레이터**입니다.
- `SimPy` 기반 이산 이벤트 시뮬레이션 엔진으로 로봇 작업 배정·충전 스케줄링 최적화
- GUI로 공장 현황을 실시간 시각화, DB 연동으로 설비 구성 변경을 무중단 반영
- 자연어로 시뮬레이션을 제어하는 AI 관제 콘솔 연동

자세한 설계 배경과 화면 구성은 [`캡디2/README.md`](./캡디2/README.md)에 정리되어 있습니다.

---

## 🧭 학습 흐름

```
C 기초 문법 (코드업)
      │
      ▼
시스템 해킹 기초 (BufferOverflow_prac)
      │
      ▼
웹 보안 — 취약점 직접 설계 & 실제 문제 풀이 (Xss_wargame_Prac, dreamhack_prac)
      │
      ▼
네트워크 프로그래밍 (PythonPortScanner)
      │
      ▼
웹 풀스택 개발 (MovieChartWeb_prac)
      │
      ▼
종합 프로젝트 — 시뮬레이션 + AI 연동 (캡디2)
```
