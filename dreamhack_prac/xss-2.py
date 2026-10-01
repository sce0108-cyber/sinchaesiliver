#!/usr/bin/python3
from flask import Flask, request, render_template
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import urllib
import os

app = Flask(__name__)
app.secret_key = os.urandom(32)

# flag.txt가 없으면(로컬 테스트 환경) 더미 문자열로 대체
try:
    FLAG = open("./flag.txt", "r").read()
except:
    FLAG = "[**FLAG**]"


# "관리자 봇" 역할: headless 크롬으로 지정된 쿠키를 넣고 url을 방문한다.
# 공격자가 심은 XSS 페이로드가 실제 브라우저(JS 실행 O)에서 동작하는지 확인하는 용도.
def read_url(url, cookie={"name": "name", "value": "value"}):
    cookie.update({"domain": "127.0.0.1"})  # 쿠키를 붙일 도메인 고정
    try:
        service = Service(executable_path="/chromedriver")
        options = webdriver.ChromeOptions()
        for _ in [
            "headless",              # 화면 없이 실행
            "window-size=1920x1080",
            "disable-gpu",
            "no-sandbox",
            "disable-dev-shm-usage",
        ]:
            options.add_argument(_)
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(3)
        driver.set_page_load_timeout(3)  # 페이지 로드 3초 제한(무한 alert 등으로 멈추는 것 방지)
        driver.get("http://127.0.0.1:8000/")  # 쿠키 추가는 같은 도메인에 먼저 접속해야 가능(Selenium 제약)
        driver.add_cookie(cookie)             # 여기서 쿠키(예: flag 값)를 브라우저에 주입
        driver.get(url)                       # 공격자가 만든 최종 URL(payload 포함)로 이동 → 이 시점에 XSS 실행
    except Exception as e:
        driver.quit()
        # return str(e)
        return False  # 타임아웃/에러 발생 시 실패로 간주(예: 무한 alert로 페이지 로드가 안 끝난 경우 등)
    driver.quit()
    return True


# 사용자가 제출한 param을 /vuln?param= 뒤에 붙여서 봇이 방문할 최종 URL을 생성
def check_xss(param, cookie={"name": "name", "value": "value"}):
    url = f"http://127.0.0.1:8000/vuln?param={urllib.parse.quote(param)}"
    return read_url(url, cookie)


@app.route("/")
def index():
    return render_template("index.html")


# 실제 XSS 취약점이 있는 페이지(추정): param 값을 이스케이프 없이 렌더링할 가능성이 높음
@app.route("/vuln")
def vuln():
    return render_template("vuln.html")


@app.route("/flag", methods=["GET", "POST"])
def flag():
    if request.method == "GET":
        return render_template("flag.html")  # 페이로드(param) 입력 폼
    elif request.method == "POST":
        param = request.form.get("param")
        # 진짜 FLAG 값을 쿠키(name=flag)에 담은 봇이 /vuln?param=<param>을 방문
        # → 여기서 XSS가 터지면 document.cookie로 FLAG를 읽어 외부로 유출 가능
        if not check_xss(param, {"name": "flag", "value": FLAG.strip()}):
            return '<script>alert("wrong??");history.go(-1);</script>'

        # 봇이 정상적으로(에러/타임아웃 없이) 페이지를 로드했다는 뜻일 뿐, 플래그를 직접 돌려주진 않음
        return '<script>alert("good");history.go(-1);</script>'


memo_text = ""  # 모든 요청이 공유하는 전역 메모(세션 구분 없음)


@app.route("/memo")
def memo():
    global memo_text
    text = request.args.get("memo", "")
    memo_text += text + "\n"  # 새 입력을 계속 누적
    return render_template("memo.html", memo=memo_text)


app.run(host="0.0.0.0", port=8000)
