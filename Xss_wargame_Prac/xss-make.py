"""
XSS 워게임 (교육용) - Flask 백엔드
=====================================
이 서버는 XSS(Cross-Site Scripting)의 동작 원리를 학습하기 위해
'일부러' 취약하게 만든 실습용 웹 애플리케이션입니다.

반드시 본인 컴퓨터(localhost)에서만 실행하세요.
실제 서비스에 이런 코드를 쓰면 안 됩니다.

실행:
    pip install flask
    python app.py
    브라우저에서 http://127.0.0.1:5000 접속
"""

from flask import Flask, request, render_template_string, redirect, url_for
import html
import re

app = Flask(__name__)

# Stored XSS 단계에서 사용할 방명록 저장소 (메모리)
guestbook = []


# ---------------------------------------------------------------------------
# 공통 레이아웃
# ---------------------------------------------------------------------------
PAGE = """
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>{{ title }}</title>
  <style>
    body { font-family: sans-serif; max-width: 760px; margin: 40px auto; padding: 0 16px; color:#222; }
    header a { margin-right: 14px; text-decoration:none; color:#2563eb; }
    .box { border:1px solid #ddd; border-radius:8px; padding:16px 20px; margin-top:20px; background:#fafafa; }
    .goal { background:#fff7ed; border:1px solid #fdba74; padding:10px 14px; border-radius:6px; }
    input[type=text]{ padding:6px 8px; width:60%; }
    button{ padding:6px 14px; cursor:pointer; }
    code{ background:#eee; padding:2px 5px; border-radius:4px; }
    .result{ margin-top:14px; padding:12px; background:#fff; border:1px dashed #bbb; border-radius:6px;}
    ul.levels li{ margin:8px 0; }
  </style>
</head>
<body>
  <header>
    <a href="/">🏠 홈</a>
    <a href="/level/1">Level 1</a>
    <a href="/level/2">Level 2</a>
    <a href="/level/3">Level 3</a>
    <a href="/level/4">Level 4</a>
  </header>
  <hr>
  {{ body|safe }}
</body>
</html>
"""


def page(title, body):
    return render_template_string(PAGE, title=title, body=body)


# ---------------------------------------------------------------------------
# 홈
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    body = """
    <h1>🧪 XSS 워게임</h1>
    <p>각 단계는 XSS가 발생하는 서로 다른 상황을 보여줍니다.
    목표는 <code>alert(1)</code> 처럼 자바스크립트를 <b>실제로 실행</b>시키는 것입니다.</p>
    <div class="box">
      <ul class="levels">
        <li><b><a href="/level/1">Level 1 — Reflected XSS</a></b>: 입력값을 필터 없이 그대로 출력</li>
        <li><b><a href="/level/2">Level 2 — Stored XSS</a></b>: 저장된 방명록이 그대로 렌더링</li>
        <li><b><a href="/level/3">Level 3 — 필터 우회 (script 차단)</a></b>: <code>&lt;script&gt;</code> 문자열을 제거</li>
        <li><b><a href="/level/4">Level 4 — 필터 우회 (blacklist)</a></b>: 여러 키워드를 막지만 허점이 있음</li>
      </ul>
    </div>
    <p style="margin-top:24px;color:#666;font-size:14px;">
      💡 각 단계 하단에 '원리 설명'과 '풀이 힌트'가 있습니다. README.md 도 함께 보세요.
    </p>
    """
    return page("XSS 워게임", body)


# ---------------------------------------------------------------------------
# Level 1 : Reflected XSS (필터 없음)
# ---------------------------------------------------------------------------
@app.route("/level/1")
def level1():
    q = request.args.get("q", "")
    # ❌ 취약점: 사용자 입력을 이스케이프 없이 HTML에 그대로 삽입
    result = f'<div class="result">검색 결과: {q}</div>' if q else ""
    body = f"""
    <h2>Level 1 — Reflected XSS</h2>
    <div class="goal">🎯 목표: 검색창에 입력한 값으로 <code>alert(1)</code> 를 실행시키세요.</div>
    <form method="get">
      <input type="text" name="q" placeholder="검색어" value="">
      <button>검색</button>
    </form>
    {result}
    <div class="box">
      <h3>원리</h3>
      <p>서버가 입력값 <code>q</code> 를 아무런 처리 없이 HTML 응답에 그대로 넣습니다.
      그래서 <code>&lt;태그&gt;</code> 를 넣으면 문자가 아니라 진짜 HTML로 해석됩니다.
      이렇게 요청에 담긴 값이 즉시 응답에 '반사'되어 실행되는 것을 <b>Reflected XSS</b> 라고 합니다.</p>
      <p>힌트: <code>&lt;script&gt;alert(1)&lt;/script&gt;</code> 또는
      <code>&lt;img src=x onerror=alert(1)&gt;</code></p>
    </div>
    """
    return page("Level 1", body)


# ---------------------------------------------------------------------------
# Level 2 : Stored XSS (방명록)
# ---------------------------------------------------------------------------
@app.route("/level/2", methods=["GET", "POST"])
def level2():
    if request.method == "POST":
        name = request.form.get("name", "익명")
        message = request.form.get("message", "")
        # ❌ 취약점: 저장한 값을 나중에 그대로 출력 -> 페이지 여는 모든 사람에게 실행됨
        guestbook.append({"name": name, "message": message})
        return redirect(url_for("level2"))

    entries = ""
    for e in guestbook:
        entries += f'<div class="result"><b>{e["name"]}</b>: {e["message"]}</div>'

    body = f"""
    <h2>Level 2 — Stored XSS</h2>
    <div class="goal">🎯 목표: 방명록에 글을 남겨, 이 페이지를 여는 사람에게 <code>alert(1)</code> 이 실행되게 하세요.</div>
    <form method="post">
      <p><input type="text" name="name" placeholder="이름"></p>
      <p><input type="text" name="message" placeholder="메시지" style="width:80%"></p>
      <button>남기기</button>
    </form>
    <h3>방명록</h3>
    {entries or '<p style="color:#888">아직 글이 없습니다.</p>'}
    <div class="box">
      <h3>원리</h3>
      <p>입력값이 서버(또는 DB)에 <b>저장</b>되고, 이후 페이지를 열 때마다 그대로 출력됩니다.
      Reflected 와 달리 한 번 심어두면 <b>그 페이지를 보는 모든 사용자</b>에게 실행되기 때문에
      영향 범위가 훨씬 큽니다. 이것이 <b>Stored(저장형) XSS</b> 입니다.</p>
      <p>힌트: 메시지 칸에 <code>&lt;img src=x onerror=alert(1)&gt;</code></p>
    </div>
    """
    return page("Level 2", body)


# ---------------------------------------------------------------------------
# Level 3 : 필터 우회 — <script> 문자열 제거
# ---------------------------------------------------------------------------
@app.route("/level/3")
def level3():
    q = request.args.get("q", "")
    # ❌ 취약한 방어: "<script" 문자열만 지운다. 다른 실행 경로는 못 막음
    filtered = re.sub(r"<script", "", q, flags=re.IGNORECASE)
    result = f'<div class="result">입력: {filtered}</div>' if q else ""
    body = f"""
    <h2>Level 3 — 필터 우회 (script 차단)</h2>
    <div class="goal">🎯 목표: 필터를 우회해서 <code>alert(1)</code> 실행. (<code>&lt;script</code> 는 지워집니다)</div>
    <form method="get">
      <input type="text" name="q" placeholder="입력">
      <button>전송</button>
    </form>
    {result}
    <div class="box">
      <h3>원리</h3>
      <p>많은 개발자가 "위험한 단어만 지우면 된다"고 생각하지만, 블랙리스트 방식은
      허점이 많습니다. <code>&lt;script&gt;</code> 없이도 JS를 실행하는 방법이 아주 많거든요.</p>
      <p>힌트: 태그의 <b>이벤트 핸들러</b>를 이용하세요.
      예) <code>&lt;img src=x onerror=alert(1)&gt;</code>,
      <code>&lt;svg onload=alert(1)&gt;</code></p>
    </div>
    """
    return page("Level 3", body)


# ---------------------------------------------------------------------------
# Level 4 : 필터 우회 — 여러 키워드 블랙리스트
# ---------------------------------------------------------------------------
@app.route("/level/4")
def level4():
    q = request.args.get("q", "")
    # ❌ 취약한 방어: 몇몇 키워드를 지우지만 대소문자/중첩으로 우회 가능
    blocked = ["<script", "onerror", "onload", "alert"]
    filtered = q
    for word in blocked:
        filtered = re.sub(re.escape(word), "", filtered, flags=re.IGNORECASE)
    result = f'<div class="result">입력: {filtered}</div>' if q else ""
    body = f"""
    <h2>Level 4 — 필터 우회 (블랙리스트)</h2>
    <div class="goal">🎯 목표: <code>&lt;script</code>, <code>onerror</code>, <code>onload</code>, <code>alert</code>
    (대소문자 무시) 가 <b>한 번</b>씩 제거됩니다. 그래도 JS를 실행하세요.</div>
    <form method="get">
      <input type="text" name="q" placeholder="입력">
      <button>전송</button>
    </form>
    {result}
    <div class="box">
      <h3>원리</h3>
      <p>필터가 키워드를 <b>딱 한 번만</b> 제거한다는 점이 허점입니다.
      단어 안에 금지어를 겹쳐 넣으면(중첩), 필터가 가운데를 지운 뒤 <b>양쪽이 붙어</b>
      다시 온전한 금지어가 됩니다. 또 <code>alert</code> 없이도 코드 실행이 가능합니다.</p>
      <p>힌트 1 (중첩): <code>onerror</code> → <code>oneronerrorror</code></p>
      <p>힌트 2 (alert 우회): <code>prompt(1)</code>, <code>confirm(1)</code>,
      또는 <code>alert</code> 을 <code>al\\u0065rt</code> 처럼 인코딩</p>
      <p>예시 정답은 README 를 참고하세요.</p>
    </div>
    """
    return page("Level 4", body)


if __name__ == "__main__":
    # debug=True 는 학습 편의용. 외부에 공개하지 마세요.
    app.run(host="127.0.0.1", port=5000, debug=True)
