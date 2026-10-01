#!/usr/bin/python3
from flask import Flask, request, render_template, make_response, redirect, url_for  # 플라스크 및 요청/응답 관련 모듈 임포트

app = Flask(__name__)  # 플라스크 앱 인스턴스 생성

try:
    FLAG = open('./flag.txt', 'r').read()  # flag.txt 파일에서 실제 플래그 읽기
except:
    FLAG = '[**FLAG**]'  # 파일이 없으면 더미 플래그 사용

users = {
    'guest': 'guest',  # guest 계정 비밀번호
    'admin': FLAG        # admin 비밀번호는 곧 플래그(직접 로그인은 불가)
}

@app.route('/')
def index():
    username = request.cookies.get('username', None)  # 쿠키에서 username 값을 그대로 읽어옴(서버 검증 없음 → 위조 가능한 핵심 취약점)
    if username:
        return render_template('index.html', text=f'Hello {username}, {"flag is " + FLAG if username == "admin" else "you are not admin"}')  # username이 admin이면 플래그 노출
    return render_template('index.html')  # 쿠키가 없으면 기본 페이지 반환

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')  # GET 요청 시 로그인 폼 페이지 반환
    elif request.method == 'POST':
        username = request.form.get('username')  # 폼에서 아이디 값 추출
        password = request.form.get('password')  # 폼에서 비밀번호 값 추출
        try:
            pw = users[username]  # users 딕셔너리에서 해당 계정의 비밀번호 조회
        except:
            return '<script>alert("not found user");history.go(-1);</script>'  # 존재하지 않는 계정이면 알림 후 뒤로가기
        if pw == password:
            resp = make_response(redirect(url_for('index')) )  # 비밀번호 일치 시 인덱스로 리다이렉트 응답 생성
            resp.set_cookie('username', username)  # 인증 정보를 서명 없이 평문 쿠키로 저장(클라이언트가 임의로 변조 가능)
            return resp
        return '<script>alert("wrong password");history.go(-1);</script>'  # 비밀번호 불일치 시 알림 후 뒤로가기

app.run(host='0.0.0.0', port=8000)  # 모든 인터페이스에서 8000번 포트로 서버 실행
