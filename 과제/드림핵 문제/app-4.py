#!/usr/bin/python3
from flask import Flask, request, render_template, make_response, redirect, url_for  # 플라스크 및 요청/응답 관련 모듈 임포트

app = Flask(__name__)  # 플라스크 앱 인스턴스 생성

try:
    FLAG = open('./flag.txt', 'r').read()  # flag.txt 파일에서 실제 플래그 읽기
except:
    FLAG = '[**FLAG**]'  # 파일이 없으면 더미 플래그 사용

users = {
    'guest': 'guest',   # guest 계정 비밀번호
    'user': 'user1234', # user 계정 비밀번호
    'admin': FLAG        # admin 비밀번호는 곧 플래그(직접 로그인은 불가)
}

session_storage = {  # sessionid -> username 매핑을 저장하는 인메모리 딕셔너리
}

@app.route('/')
def index():
    session_id = request.cookies.get('sessionid', None)  # 쿠키에서 sessionid 값 추출
    try:
        username = session_storage[session_id]  # 세션 저장소에서 해당 세션의 사용자명 조회
    except KeyError:
        return render_template('index.html')  # 세션이 없으면 로그인 안 된 기본 페이지 반환

    return render_template('index.html', text=f'Hello {username}, {"flag is " + FLAG if username == "admin" else "you are not admin"}')  # admin이면 플래그 노출, 아니면 안내 문구

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
            session_id = os.urandom(4).hex()  # 4바이트(32비트) 난수로 세션 ID 생성 → 경우의 수가 적어 취약
            session_storage[session_id] = username  # 세션 저장소에 세션ID-사용자명 등록
            resp.set_cookie('sessionid', session_id)  # 응답 쿠키에 세션ID 설정
            return resp
        return '<script>alert("wrong password");history.go(-1);</script>'  # 비밀번호 불일치 시 알림 후 뒤로가기

if __name__ == '__main__':
    import os  # os 모듈 임포트(난수 생성용)
    session_storage[os.urandom(1).hex()] = 'admin'  # admin 세션ID를 단 1바이트(256가지)로만 생성 → 브루트포싱으로 알아낼 수 있는 핵심 취약점
    print(session_storage)  # 콘솔에 세션 저장소 내용 출력(디버깅용, 실제로는 노출되면 안 됨)
    app.run(host='0.0.0.0', port=8000)  # 모든 인터페이스에서 8000번 포트로 서버 실행
