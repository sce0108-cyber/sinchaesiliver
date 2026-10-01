#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scanner_level1.py - 순차(Sequential) TCP 포트 스캐너

[동작 원리]
포트 하나하나에 대해 TCP 연결을 시도해보고,
연결이 되면 OPEN, 안 되면 CLOSED 로 판단한다.

[주의] 본인 소유이거나 스캔이 허가된 호스트에만 사용할 것!
       (127.0.0.1, 직접 띄운 서버, scanme.nmap.org 등)

실행: python3 scanner_level1.py
"""

import socket
import time


def scan_port(host: str, port: int, timeout: float = 1.0) -> bool:
    """
    포트 하나에 TCP 연결을 시도한다.

    socket.AF_INET   -> IPv4 주소 체계를 쓰겠다
    socket.SOCK_STREAM -> TCP를 쓰겠다 (UDP는 SOCK_DGRAM)
    settimeout(1)    -> 1초 안에 응답 없으면 포기 (없으면 OS 기본값으로 수십 초 대기)
    connect_ex()     -> 연결 성공 시 0, 실패 시 에러번호(errno)를 '리턴'한다.
                        connect()와 달리 예외를 던지지 않아서 반복문에 쓰기 좋다.
    """
    # with 문을 쓰면 블록이 끝날 때 소켓이 자동으로 close 된다 (파일 디스크립터 누수 방지)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        try:
            result = sock.connect_ex((host, port))
            return result == 0
        except socket.error:
            # 호스트 자체에 문제가 있는 경우 등
            return False


def main() -> None:
    target = input("Target IP/domain (예: 127.0.0.1): ").strip() or "127.0.0.1"
    port_range = input("Port range (예: 1-100): ").strip() or "1-100"

    # "1-100" 형태를 숫자 두 개로 분리
    start_port, end_port = (int(x) for x in port_range.split("-"))

    # 도메인을 입력했을 수도 있으니 IP로 변환 (DNS 조회)
    try:
        ip = socket.gethostbyname(target)
    except socket.gaierror:
        print(f"[!] '{target}' 의 주소를 찾을 수 없습니다.")
        return

    print(f"\nTarget: {target} ({ip})")
    print(f"Scanning ports {start_port}-{end_port}...\n")

    started = time.perf_counter()
    open_ports = []

    for port in range(start_port, end_port + 1):
        if scan_port(ip, port):
            print(f"Port {port}: OPEN")
            open_ports.append(port)
        else:
            print(f"Port {port}: CLOSED")

    elapsed = time.perf_counter() - started
    total = end_port - start_port + 1
    print(f"\nScan complete in {elapsed:.2f}s. "
          f"{len(open_ports)} open port(s) found out of {total}.")


if __name__ == "__main__":
    main()