#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scanner.py - 멀티스레드 TCP 포트 스캐너 (Level 2)

[사용 예시]
    python3 scanner.py --host 127.0.0.1 --ports 1-1000
    python3 scanner.py --host 127.0.0.1 --ports 22,80,443 --threads 100
    python3 scanner.py --host 127.0.0.1 --ports 1-1000 --benchmark
    python3 scanner.py --host 127.0.0.1 --ports 1-100 --show-closed

[주의] 본인 소유이거나 스캔이 허가된 호스트에만 사용할 것!
"""

import argparse
import socket
import sys
import time
from concurrent.futures import ThreadPoolExecutor

# ---------------------------------------------------------------------------
# 1. 서비스 이름 매핑용 테이블
#    socket.getservbyport()가 OS의 /etc/services를 참조하는데,
#    환경에 따라 없는 포트가 있어서 자주 쓰는 것들은 직접 정의해둔다.
# ---------------------------------------------------------------------------
COMMON_SERVICES = {
    20: "ftp-data", 21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp",
    53: "dns", 67: "dhcp", 69: "tftp", 80: "http", 110: "pop3",
    123: "ntp", 135: "msrpc", 139: "netbios-ssn", 143: "imap",
    161: "snmp", 389: "ldap", 443: "https", 445: "smb", 465: "smtps",
    587: "submission", 993: "imaps", 995: "pop3s",
    1433: "mssql", 1521: "oracle", 2049: "nfs",
    3000: "node/dev-server", 3306: "mysql", 3389: "rdp",
    5000: "flask/upnp", 5432: "postgresql", 5900: "vnc",
    6379: "redis", 8000: "http-alt", 8080: "http-proxy",
    8443: "https-alt", 9200: "elasticsearch", 27017: "mongodb",
}


def guess_service(port: int) -> str:
    """포트 번호로 서비스 이름을 추정한다."""
    if port in COMMON_SERVICES:
        return COMMON_SERVICES[port]
    try:
        # OS에 등록된 서비스 이름을 조회 (없으면 OSError)
        return socket.getservbyport(port, "tcp")
    except OSError:
        return "unknown"


# ---------------------------------------------------------------------------
# 2. 포트 하나를 검사하는 함수 (스캐너의 심장)
# ---------------------------------------------------------------------------
def scan_port(host: str, port: int, timeout: float) -> tuple:
    """
    반환값: (포트번호, 열림여부)

    connect_ex()는 성공하면 0, 실패하면 errno를 반환한다.
    - 0            : 3-Way Handshake 성공 -> OPEN
    - ECONNREFUSED : 상대가 RST로 거절 -> CLOSED
    - timeout      : 아무 응답 없음 -> 방화벽이 막았을 가능성(filtered)
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        try:
            return port, sock.connect_ex((host, port)) == 0
        except socket.error:
            return port, False


# ---------------------------------------------------------------------------
# 3. 두 가지 스캔 방식 (속도 비교용)
# ---------------------------------------------------------------------------
def scan_sequential(host: str, ports: list, timeout: float) -> list:
    """포트를 하나씩 순서대로 검사한다. 느리다."""
    return [p for p, is_open in (scan_port(host, p, timeout) for p in ports) if is_open]


def scan_threaded(host: str, ports: list, timeout: float, workers: int) -> list:
    """
    ThreadPoolExecutor로 여러 포트를 동시에 검사한다.

    포트 스캔은 CPU 연산이 아니라 '응답을 기다리는' I/O 작업이라서
    파이썬 GIL이 있어도 스레드로 큰 이득을 본다.
    (기다리는 동안 GIL이 다른 스레드에 넘어감)
    """
    open_ports = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        # executor.map은 결과를 입력 순서대로 돌려준다
        for port, is_open in executor.map(lambda p: scan_port(host, p, timeout), ports):
            if is_open:
                open_ports.append(port)
    return sorted(open_ports)


# ---------------------------------------------------------------------------
# 4. 입력값 파싱 유틸
# ---------------------------------------------------------------------------
def parse_ports(spec: str) -> list:
    """
    "80"        -> [80]
    "1-1000"    -> [1, 2, ..., 1000]
    "22,80,443" -> [22, 80, 443]
    "1-100,443" -> [1..100, 443]
    """
    ports = set()
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            start_str, end_str = chunk.split("-", 1)
            start, end = int(start_str), int(end_str)
            if start > end:
                start, end = end, start
            ports.update(range(start, end + 1))
        else:
            ports.add(int(chunk))
    valid = sorted(p for p in ports if 1 <= p <= 65535)
    if not valid:
        raise ValueError("유효한 포트가 없습니다 (1-65535)")
    return valid


def print_results(open_ports: list, total: int, elapsed: float, show_closed: bool, ports: list) -> None:
    for port in open_ports:
        print(f"Port {port:>5} ({guess_service(port)}): OPEN")

    if show_closed:
        closed = [p for p in ports if p not in set(open_ports)]
        for port in closed:
            print(f"Port {port:>5} ({guess_service(port)}): CLOSED")

    print(f"\nScan finished in {elapsed:.2f}s "
          f"(open: {len(open_ports)}, closed: {total - len(open_ports)})")


# ---------------------------------------------------------------------------
# 5. CLI 진입점
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="간단한 TCP 포트 스캐너 (교육용). 허가된 호스트에만 사용하세요.",
    )
    parser.add_argument("--host", required=True, help="대상 IP 또는 도메인 (예: 127.0.0.1)")
    parser.add_argument("--ports", default="1-1024", help="포트 범위 (예: 1-1000, 22,80,443)")
    parser.add_argument("--threads", type=int, default=50, help="동시 스레드 개수 (기본 50)")
    parser.add_argument("--timeout", type=float, default=1.0, help="포트당 타임아웃 초 (기본 1.0)")
    parser.add_argument("--show-closed", action="store_true", help="닫힌 포트도 출력")
    parser.add_argument("--benchmark", action="store_true",
                        help="순차 스캔 vs 스레드 스캔 소요 시간 비교")
    args = parser.parse_args()

    # 도메인 -> IP 변환
    try:
        ip = socket.gethostbyname(args.host)
    except socket.gaierror:
        print(f"[!] '{args.host}' 주소를 찾을 수 없습니다.")
        sys.exit(1)

    try:
        ports = parse_ports(args.ports)
    except ValueError as e:
        print(f"[!] 포트 형식 오류: {e}")
        sys.exit(1)

    # --- 벤치마크 모드 -----------------------------------------------------
    if args.benchmark:
        print(f"[Benchmark] {args.host} ({ip}), {len(ports)}개 포트, "
              f"timeout={args.timeout}s\n")

        t0 = time.perf_counter()
        seq_result = scan_sequential(ip, ports, args.timeout)
        seq_time = time.perf_counter() - t0
        print(f"1) 순차 스캔       : {seq_time:8.2f}s (open: {len(seq_result)})")

        t0 = time.perf_counter()
        thr_result = scan_threaded(ip, ports, args.timeout, args.threads)
        thr_time = time.perf_counter() - t0
        print(f"2) 스레드 {args.threads}개 스캔 : {thr_time:8.2f}s (open: {len(thr_result)})")

        if thr_time > 0:
            print(f"\n=> 약 {seq_time / thr_time:.1f}배 빨라짐")
        print(f"=> 열린 포트: {thr_result}")
        return

    # --- 일반 스캔 모드 ----------------------------------------------------
    print(f"Scanning {args.host} ({ip}) "
          f"(ports {args.ports}) with {args.threads} threads...\n")

    started = time.perf_counter()
    open_ports = scan_threaded(ip, ports, args.timeout, args.threads)
    elapsed = time.perf_counter() - started

    print_results(open_ports, len(ports), elapsed, args.show_closed, ports)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] 사용자가 스캔을 중단했습니다.")
        sys.exit(130)