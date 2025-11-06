#!/usr/bin/env python3
"""
System Resource Monitor - Main Application
실시간 시스템 리소스 모니터링 및 PDF 리포트 생성

사용법:
    python main.py

5분간 모니터링 후 자동으로 PDF 리포트를 생성합니다.
"""

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from monitor import SystemMonitor
from report_generator import ReportGenerator
import threading
import time
from datetime import datetime, timedelta
import webbrowser
import os

# Flask 앱 설정
app = Flask(__name__)
app.config['SECRET_KEY'] = 'system-monitor-secret-key-2024'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# 전역 변수
monitor = SystemMonitor()
monitoring_active = False
monitoring_thread = None
MONITORING_DURATION = 300  # 5분 (초 단위)

@app.route('/')
def index():
    """메인 페이지"""
    system_info = monitor.get_system_info()
    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return render_template('dashboard.html',
                         system_info=system_info,
                         start_time=start_time)

def monitoring_task():
    """백그라운드 모니터링 작업"""
    global monitoring_active

    print("모니터링 시작...")
    monitor.start_monitoring()
    start_time = time.time()
    end_time = start_time + MONITORING_DURATION

    while monitoring_active and time.time() < end_time:
        # 시스템 데이터 수집
        data = monitor.collect_all_data()

        # 클라이언트에 데이터 전송
        socketio.emit('system_data', data)

        # 시간 정보 전송
        elapsed = time.time() - start_time
        remaining = max(0, MONITORING_DURATION - elapsed)

        duration_str = str(timedelta(seconds=int(elapsed))).split('.')[0]
        remaining_str = f"{int(remaining // 60):02d}:{int(remaining % 60):02d}"

        socketio.emit('time_update', {
            'duration': duration_str,
            'remaining': remaining_str
        })

        # 1초 대기
        socketio.sleep(1)

    # 모니터링 완료
    if monitoring_active:
        print("\n모니터링 완료! PDF 리포트 생성 중...")

        # PDF 생성
        system_info = monitor.get_system_info()
        report_gen = ReportGenerator(monitor, system_info)
        pdf_path = report_gen.generate_report()

        # 절대 경로로 변환
        pdf_abs_path = os.path.abspath(pdf_path)

        print(f"\n✓ PDF 리포트가 생성되었습니다: {pdf_abs_path}")

        # 클라이언트에 완료 알림
        socketio.emit('monitoring_complete', {
            'message': f'모니터링 완료! PDF 리포트: {pdf_abs_path}',
            'pdf_path': pdf_abs_path
        })

        monitoring_active = False

@socketio.on('connect')
def handle_connect():
    """클라이언트 연결"""
    global monitoring_active, monitoring_thread

    print(f"클라이언트 연결됨")

    # 모니터링이 아직 시작되지 않았으면 시작
    if not monitoring_active:
        monitoring_active = True
        monitoring_thread = threading.Thread(target=monitoring_task)
        monitoring_thread.daemon = True
        monitoring_thread.start()

@socketio.on('disconnect')
def handle_disconnect():
    """클라이언트 연결 해제"""
    print("클라이언트 연결 해제됨")

def open_browser():
    """브라우저 자동 열기"""
    time.sleep(1.5)  # 서버 시작 대기
    webbrowser.open('http://localhost:5000')

def main():
    """메인 함수"""
    print("=" * 60)
    print("시스템 리소스 모니터 시작")
    print("=" * 60)
    print()
    print("📊 실시간 대시보드: http://localhost:5000")
    print("⏱️  모니터링 시간: 5분")
    print("📄 PDF 리포트: 자동 생성")
    print()
    print("브라우저가 자동으로 열립니다...")
    print("종료하려면 Ctrl+C를 누르세요.")
    print()

    # 브라우저 자동 열기
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()

    try:
        # Flask 서버 시작
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n\n모니터링이 중단되었습니다.")
        global monitoring_active
        monitoring_active = False

        # 중단되어도 지금까지의 데이터로 PDF 생성
        if len(monitor.data_history['timestamps']) > 0:
            print("지금까지 수집된 데이터로 PDF를 생성합니다...")
            system_info = monitor.get_system_info()
            report_gen = ReportGenerator(monitor, system_info)
            pdf_path = report_gen.generate_report()
            pdf_abs_path = os.path.abspath(pdf_path)
            print(f"✓ PDF 리포트가 생성되었습니다: {pdf_abs_path}")

if __name__ == '__main__':
    main()
