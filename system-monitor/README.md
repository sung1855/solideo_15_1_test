# 시스템 리소스 모니터 📊

실시간으로 시스템 리소스를 모니터링하고 시각화하는 웹 기반 대시보드입니다. 5분간 자동으로 모니터링한 후 상세한 PDF 리포트를 생성합니다.

## 주요 기능 ✨

### 모니터링 항목
- **CPU**
  - 전체 사용률 및 코어별 사용률
  - CPU 온도 (지원되는 시스템)
  - 실시간 주파수

- **메모리 (RAM)**
  - 사용률 및 사용량 (GB)
  - 사용 가능한 메모리
  - Swap 메모리 정보

- **GPU**
  - GPU 사용률
  - GPU 온도
  - GPU 메모리 사용량

- **디스크**
  - 디스크 사용률
  - 실시간 읽기/쓰기 속도 (MB/s)

- **네트워크**
  - 업로드/다운로드 속도 (MB/s)
  - 총 전송량

- **프로세스**
  - CPU 사용률 상위 5개 프로세스
  - 각 프로세스의 메모리 사용률

### 기능
- 🔄 **실시간 모니터링** (1초 간격)
- 📈 **인터랙티브 차트** (Plotly 기반)
- 🎨 **색상 코딩** (정상/경고/위험)
- ⏱️ **자동 모니터링** (5분)
- 📄 **PDF 리포트 자동 생성**
- 📊 **통계 요약** (평균, 최소, 최대값)

## 설치 방법 🛠️

### 1. Python 요구사항
Python 3.8 이상이 필요합니다.

### 2. 의존성 설치

```bash
cd system-monitor
pip install -r requirements.txt
```

### 3. 필요한 라이브러리
- Flask - 웹 프레임워크
- Flask-SocketIO - 실시간 통신
- psutil - 시스템 정보
- GPUtil - GPU 정보
- Plotly - 인터랙티브 차트
- Matplotlib - 그래프 생성
- ReportLab - PDF 생성

## 사용 방법 🚀

### 기본 실행

```bash
python main.py
```

또는

```bash
python3 main.py
```

### 실행 흐름

1. **프로그램 실행**
   - 터미널에서 `python main.py` 실행
   - Flask 서버가 시작됩니다 (포트 5000)

2. **대시보드 자동 열림**
   - 브라우저가 자동으로 `http://localhost:5000` 열림
   - 수동 접속: 웹 브라우저에서 `http://localhost:5000` 입력

3. **모니터링 시작**
   - 자동으로 5분간 모니터링 시작
   - 실시간으로 그래프와 수치가 업데이트됨

4. **PDF 리포트 생성**
   - 5분 후 자동으로 `reports/` 폴더에 PDF 생성
   - 파일명: `system_monitor_report_YYYYMMDD_HHMMSS.pdf`

5. **중간 종료**
   - `Ctrl+C`로 언제든 종료 가능
   - 종료 시 지금까지 수집된 데이터로 PDF 생성

## 프로젝트 구조 📁

```
system-monitor/
├── main.py                  # 메인 실행 파일
├── monitor.py               # 시스템 데이터 수집 모듈
├── report_generator.py      # PDF 리포트 생성 모듈
├── requirements.txt         # 의존성 목록
├── README.md               # 문서 (이 파일)
│
├── templates/
│   └── dashboard.html      # 웹 대시보드 HTML
│
├── static/
│   ├── css/
│   │   └── style.css       # 스타일시트
│   └── js/
│       └── dashboard.js    # 클라이언트 JavaScript
│
└── reports/                # 생성된 PDF 저장 폴더
    └── system_monitor_report_*.pdf
```

## PDF 리포트 내용 📄

생성된 PDF 리포트에는 다음 정보가 포함됩니다:

1. **표지 페이지**
   - 모니터링 시작/종료 시간
   - 시스템 정보 (OS, CPU, 메모리 등)
   - 주요 통계 요약

2. **CPU 및 메모리 페이지**
   - CPU 사용률 그래프
   - CPU 온도 그래프
   - 메모리 사용률 그래프
   - 메모리 사용량 그래프

3. **GPU 및 디스크 페이지**
   - GPU 사용률 그래프
   - GPU 온도 그래프
   - 디스크 사용률 그래프
   - 디스크 I/O 속도 그래프

4. **네트워크 페이지**
   - 네트워크 전송 속도 그래프
   - 업로드/다운로드 통계

5. **통계 요약 페이지**
   - 모든 메트릭의 평균/최소/최대값
   - 종합 분석 정보

## 설정 변경 ⚙️

### 모니터링 시간 변경

`main.py` 파일에서 다음 변수를 수정:

```python
MONITORING_DURATION = 300  # 5분 (초 단위)
```

예시:
- 3분: `MONITORING_DURATION = 180`
- 10분: `MONITORING_DURATION = 600`

### 샘플링 간격 변경

`main.py`의 `monitoring_task()` 함수에서:

```python
socketio.sleep(1)  # 1초 대기
```

예시:
- 2초 간격: `socketio.sleep(2)`
- 0.5초 간격: `socketio.sleep(0.5)`

### 포트 변경

`main.py`의 마지막 부분:

```python
socketio.run(app, host='0.0.0.0', port=5000, debug=False)
```

## 문제 해결 🔧

### GPU 정보가 표시되지 않음
- NVIDIA GPU가 없거나 드라이버가 설치되지 않은 경우 정상입니다
- "N/A"로 표시되며 나머지 기능은 정상 작동합니다

### CPU 온도가 표시되지 않음
- 모든 시스템에서 온도 센서를 지원하지 않습니다
- Linux에서 `lm-sensors` 패키지 설치 권장:
  ```bash
  sudo apt-get install lm-sensors
  ```

### 포트 5000이 이미 사용 중
- 다른 프로그램이 포트 5000을 사용 중일 수 있습니다
- `main.py`에서 포트 번호를 변경하세요 (예: 5001, 8080 등)

### 권한 오류
- 일부 시스템 정보는 관리자 권한이 필요할 수 있습니다
- Linux/Mac: `sudo python main.py`
- Windows: 관리자 권한으로 실행

## 기술 스택 💻

- **Backend**: Flask, Flask-SocketIO
- **Frontend**: HTML5, CSS3, JavaScript
- **차트**: Plotly.js
- **시스템 정보**: psutil, GPUtil
- **PDF 생성**: Matplotlib, ReportLab
- **실시간 통신**: Socket.IO

## 시스템 요구사항 💾

- **OS**: Windows, Linux, macOS
- **Python**: 3.8 이상
- **RAM**: 최소 512MB
- **디스크**: 100MB 여유 공간
- **브라우저**: Chrome, Firefox, Safari, Edge (최신 버전)

## 라이선스 📝

MIT License

## 기여 🤝

버그 리포트나 기능 제안은 언제든 환영합니다!

## 스크린샷 📸

대시보드는 다음을 제공합니다:
- 실시간 차트 업데이트
- 색상 코딩된 상태 표시
- 반응형 디자인
- 프로세스 테이블
- 시간 추적

---

**개발자**: System Monitor Team
**버전**: 1.0.0
**날짜**: 2024
