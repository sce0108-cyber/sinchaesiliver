# [CSRF] csrf-2 문제 풀이 Write-up

## 문제 요약

로그인 기능이 있는 Flask 앱. `admin` 계정의 비밀번호가 곧 FLAG (`users = {'admin': FLAG}`). `/flag` (POST)에 페이로드(`param`)를 제출하면, 서버가 `admin` 권한의 세션 쿠키를 만들어서 봇에게 쥐어준 뒤 `/vuln?param=<param>`을 방문시킴. 이 봇이 admin 세션으로 어떤 행동을 하게 만드는 게 목표.

- `/vuln`: 템플릿 렌더링 없이, 필터링만 거친 `param`을 그대로 HTTP 응답 본문으로 돌려줌
- `/change_password`: **GET** 방식으로 `pw` 값을 받아서, 요청을 보낸 사람(쿠키 주인)의 비밀번호를 그 값으로 덮어씀 — 로그인 여부만 확인하고 "진짜 본인이 요청한 게 맞는지" 확인하는 절차(CSRF 토큰 등)가 없음

## 필터 확인

```python
xss_filter = ["frame", "script", "on"]
```

`param`에서 위 세 단어가 포함된 부분을 통째로 `*`로 뭉개버림. 즉:
- `<script>` → `<*>` 로 깨짐
- `<iframe>` → `<*>` 로 깨짐 (`"frame"` 포함)
- `onerror`, `onload` 등 → `*` 로 깨짐 (`"on"` 포함)

## 시도 1 — 검토만 하고 안 씀: `onerror` (xss-2에서 먹혔던 방법)

```html
<img src=x onerror="fetch('/memo?memo='+document.cookie)">
```

**왜 여기선 안 통하는가**: `onerror`라는 단어 자체에 `"on"`이 포함돼 있어서 필터에 걸려 `*error`로 깨짐 → 이벤트 핸들러로 인식되지 않아 실행 자체가 안 됨. xss-2와 필터 대상이 다르다는 걸 먼저 확인하고 다른 접근이 필요하다고 판단.

## 성공한 방법 — `<img src="...">` 로 GET 요청 강제 발생 (CSRF)

```html
<img src="/change_password?pw=hacked1234">
```

**핵심 아이디어 (XSS와 목표 자체가 다름)**:
- XSS의 목표: 쿠키를 **읽어서** 외부로 **보내는 코드를 실행**시키는 것 → 코드 실행이 필수라서 `<script>`가 막히면 `onerror` 같은 "실행 수단"이 꼭 필요했음.
- CSRF의 목표: 코드 실행이 **전혀 필요 없음**. 이미 로그인된 사람(admin 봇)이 특정 주소로 **요청을 한 번 보내게만** 만들면 끝.
- 브라우저는 `<img src="주소">`를 만나면 `onerror` 유무와 상관없이 그 주소로 요청을 시도하고, 이때 쿠키를 자동으로 함께 보냄. `/change_password`는 GET 요청 + 쿠키만으로 동작하므로, 이미지 로드 성공/실패는 상관없이 요청은 이미 서버에 도달해서 처리됨.
- `"frame"`, `"script"`, `"on"` 중 어느 단어도 이 페이로드엔 없어서 필터에 전혀 걸리지 않음.

## 익스플로잇 단계

1. 원하는 임의의 비밀번호를 하나 정한다 (예: `hacked1234`)
2. `/flag`의 `param`에 페이로드 제출:
   ```html
   <img src="/change_password?pw=hacked1234">
   ```
3. 봇(admin 세션 보유)이 `/vuln`을 방문 → 페이지에 박힌 `<img>` 태그가 `/change_password?pw=hacked1234`로 GET 요청 → admin 비밀번호가 `hacked1234`로 변경됨
4. `/login`에서 `username: admin`, `password: hacked1234` (2번과 반드시 동일한 값)로 로그인
5. `/`에서 FLAG 확인 → `DH{c57d0dc12bb9ff023faf9a0e2b49e470a77271ef}`

## 배운 점 / 다음에 비슷한 문제 만나면 체크할 것

1. **XSS 필터와 CSRF 방어는 별개다.** 이 문제는 XSS용 필터(`frame`/`script`/`on`)는 갖춰놨지만, 상태를 변경하는 요청(`/change_password`)을 GET으로 열어두고 CSRF 토큰 같은 별도 검증이 없어서 필터와 무관하게 뚫림. "XSS를 막았으니 안전하다"고 착각하면 안 됨.
2. **상태를 변경하는 액션(비밀번호 변경, 삭제 등)이 GET으로 열려 있으면 그 자체로 위험 신호.** `<img>`, `<a>`, 자동 제출 `<form>` 등 코드 실행 없이도 요청을 강제로 보낼 수 있는 수단이 많음.
3. 블랙리스트 필터(`"on"` 같은 부분 문자열 치환)는 **의도한 것(XSS 이벤트 핸들러)만 막고, 전혀 다른 종류의 공격(CSRF)에는 무방비**일 수 있다는 걸 실감함.
