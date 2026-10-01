#!/usr/bin/python3
from flask import Flask, request, render_template, make_response, redirect, url_for
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import urllib
import os

app = Flask(__name__)
app.secret_key = os.urandom(32)

CHROMIUM_BIN = os.environ.get("CHROMIUM_BIN", "/usr/bin/chromium")
CHROMEDRIVER_PATH = os.environ.get("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")

# flag.txt 없으면(로컬 테스트) 더미 문자열로 대체
try:
    FLAG = open("./flag.txt", "r").read()
except:
    FLAG = "[**FLAG**]"

# 계정 저장소: admin 비밀번호가 바로 FLAG로 되어있음 -> admin 비밀번호를 알아내면 바로 FLAG
users = {
    'guest': 'guest',
    'admin': FLAG
}

session_storage = {}  # {세션ID: 유저이름} 형태의 아주 단순한 "로그인 상태" 저장소 (DB 대신 메모리에 저장)

# "관리자 봇" 역할: 지정된 쿠키(세션ID)를 들고 url을 방문해서, 그 세션 권한으로 실제 행동을 하게 만듦
def read_url(url, cookie={"name": "name", "value": "value"}):
    cookie.update({"domain": "127.0.0.1"})
    driver = None
    try:
        options = webdriver.ChromeOptions()
        options.binary_location = CHROMIUM_BIN
        for argument in [
            "--headless",
            "--window-size=1920,1080",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ]:
            options.add_argument(argument)
        service = Service(executable_path=CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(3)
        driver.set_page_load_timeout(3)
        driver.get("http://127.0.0.1:8000/")
        driver.add_cookie(cookie)   # 여기서 세션 쿠키(sessionid=admin 세션)를 주입 -> 이후 요청은 "관리자로 로그인된 상태"가 됨
        driver.get(url)             # 공격자가 만든 param이 들어간 /vuln 페이지 방문 -> 여기서 CSRF 페이로드 실행
    except Exception as e:
        print(str(e))
        return False
    finally:
        if driver is not None:
            driver.quit()
    return True


# 사용자가 제출한 param을 /vuln?param= 뒤에 붙여서 봇이 방문할 최종 URL 생성
def check_csrf(param, cookie={"name": "name", "value": "value"}):
    url = f"http://127.0.0.1:8000/vuln?param={urllib.parse.quote(param)}"
    return read_url(url, cookie)


@app.route("/")
def index():
    session_id = request.cookies.get('sessionid', None)
    try:
        username = session_storage[session_id]  # 내 쿠키(sessionid)로 로그인된 유저이름 조회
    except KeyError:
        return render_template('index.html', text='please login')

    # admin으로 로그인되어 있을 때만 화면에 FLAG를 보여줌
    return render_template('index.html', text=f'Hello {username}, {"flag is " + FLAG if username == "admin" else "you are not an admin"}')


# 여기는 XSS가 아니라 CSRF용 취약점 페이지: 템플릿 렌더링 없이 필터링만 거친 param을 그대로 응답으로 돌려줌
@app.route("/vuln")
def vuln():
    param = request.args.get("param", "").lower()
    xss_filter = ["frame", "script", "on"]  # "iframe", "<script>", "onerror" 등을 막으려는 필터
    for _ in xss_filter:
        param = param.replace(_, "*")  # 해당 문자열이 포함되면 통째로 *로 뭉개버림 (문자만 지우는 게 아니라 단어를 깨버림)
    return param
    # 주의: "on"이 필터링되니 onerror 같은 JS 이벤트 핸들러 트릭은 못 씀.
    # 하지만 <img src="..."> 처럼 태그가 스스로 요청을 보내는 것(=CSRF)은 "on"/"script"/"frame" 없이도 가능!


@app.route("/flag", methods=["GET", "POST"])
def flag():
    if request.method == "GET":
        return render_template("flag.html")  # 페이로드(param) 입력 폼
    elif request.method == "POST":
        param = request.form.get("param", "")
        session_id = os.urandom(16).hex()
        session_storage[session_id] = 'admin'  # 이 세션ID는 관리자 권한으로 등록됨
        # 봇이 "admin 세션 쿠키"를 들고 /vuln?param=<param>을 방문
        # -> 필터를 뚫고 여기서 admin 권한으로 어떤 요청(예: 비밀번호 변경)을 강제로 보내게 만드는 게 목표(CSRF)
        if not check_csrf(param, {"name":"sessionid", "value": session_id}):
            return '<script>alert("wrong??");history.go(-1);</script>'

        return '<script>alert("good");history.go(-1);</script>'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            pw = users[username]
        except:
            return '<script>alert("not found user");history.go(-1);</script>'
        if pw == password:
            resp = make_response(redirect(url_for('index')) )
            session_id = os.urandom(8).hex()
            session_storage[session_id] = username
            resp.set_cookie('sessionid', session_id)  # 로그인 성공 -> 내 브라우저에도 세션 쿠키 발급
            return resp
        return '<script>alert("wrong password");history.go(-1);</script>'


# 진짜 노려야 할 행동: 로그인된 사람(=쿠키 주인) 명의로 비밀번호를 바꿔버림
# CSRF 공격 포인트: 이 라우트가 GET이라서 <img src="/change_password?pw=..."> 같은 태그만으로도 요청이 그대로 실행됨
@app.route("/change_password")
def change_password():
    pw = request.args.get("pw", "")
    session_id = request.cookies.get('sessionid', None)
    try:
        username = session_storage[session_id]  # 지금 요청을 보낸 쿠키 주인이 누구인지 확인 (admin 봇이면 username="admin")
    except KeyError:
        return render_template('index.html', text='please login')

    users[username] = pw  # 그 유저의 비밀번호를 공격자가 지정한 pw로 덮어씀 (admin이면 admin 비번이 바뀜)
    return 'Done'

app.run(host="0.0.0.0", port=8000)
