"""
PDF Report Generator
모니터링 데이터를 기반으로 PDF 리포트 생성
"""

import matplotlib
matplotlib.use('Agg')  # GUI 없이 사용
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime
import os
from typing import Dict, Any
import numpy as np

class ReportGenerator:
    """PDF 리포트 생성 클래스"""

    def __init__(self, monitor, system_info: Dict[str, Any]):
        self.monitor = monitor
        self.system_info = system_info
        self.data_history = monitor.data_history
        self.stats = monitor.get_statistics()

    def generate_report(self, filename: str = None) -> str:
        """PDF 리포트 생성"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"reports/system_monitor_report_{timestamp}.pdf"

        # 디렉토리 생성
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        # PDF 생성
        with PdfPages(filename) as pdf:
            # 페이지 1: 표지 및 요약
            self._create_title_page(pdf)

            # 페이지 2: CPU 및 메모리
            self._create_cpu_memory_page(pdf)

            # 페이지 3: GPU 및 디스크
            self._create_gpu_disk_page(pdf)

            # 페이지 4: 네트워크
            self._create_network_page(pdf)

            # 페이지 5: 통계 요약
            self._create_statistics_page(pdf)

            # 메타데이터
            d = pdf.infodict()
            d['Title'] = '시스템 리소스 모니터링 리포트'
            d['Author'] = 'System Monitor'
            d['Subject'] = '시스템 리소스 모니터링 결과'
            d['Keywords'] = 'System Monitoring Performance'
            d['CreationDate'] = datetime.now()

        return filename

    def _create_title_page(self, pdf):
        """표지 페이지 생성"""
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle('시스템 리소스 모니터링 리포트', fontsize=24, fontweight='bold', y=0.85)

        # 시스템 정보 텍스트
        info_text = f"""
모니터링 시작: {self.monitor.start_time.strftime('%Y-%m-%d %H:%M:%S')}
모니터링 종료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
모니터링 기간: {self.monitor.get_monitoring_duration()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

시스템 정보:

운영체제: {self.system_info.get('os', 'N/A')}
프로세서: {self.system_info.get('processor', 'N/A')[:60]}
CPU 코어: {self.system_info.get('cpu_count', 'N/A')} 코어 / {self.system_info.get('cpu_threads', 'N/A')} 스레드
최대 주파수: {self.system_info.get('cpu_freq_max', 'N/A')}
총 메모리: {self.system_info.get('total_memory', 'N/A')}
호스트명: {self.system_info.get('hostname', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

리포트 요약:

총 데이터 포인트: {len(self.data_history['timestamps'])}개
샘플링 간격: 1초
"""

        # 통계 요약 추가
        if 'cpu_percent' in self.stats:
            info_text += f"\nCPU 평균 사용률: {self.stats['cpu_percent']['avg']:.1f}%"
            info_text += f"\nCPU 최대 사용률: {self.stats['cpu_percent']['max']:.1f}%"

        if 'memory_percent' in self.stats:
            info_text += f"\n메모리 평균 사용률: {self.stats['memory_percent']['avg']:.1f}%"
            info_text += f"\n메모리 최대 사용률: {self.stats['memory_percent']['max']:.1f}%"

        plt.text(0.5, 0.5, info_text, ha='center', va='center',
                fontsize=11, family='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

        plt.axis('off')
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_cpu_memory_page(self, pdf):
        """CPU 및 메모리 페이지 생성"""
        fig, axes = plt.subplots(2, 2, figsize=(11, 8.5))
        fig.suptitle('CPU 및 메모리 모니터링', fontsize=16, fontweight='bold')

        timestamps = range(len(self.data_history['timestamps']))

        # CPU 사용률 그래프
        if self.data_history['cpu_percent']:
            ax = axes[0, 0]
            ax.plot(timestamps, self.data_history['cpu_percent'],
                   color='#667eea', linewidth=1.5, label='CPU')
            ax.fill_between(timestamps, self.data_history['cpu_percent'],
                           alpha=0.3, color='#667eea')
            ax.set_title('CPU 사용률 (%)', fontweight='bold')
            ax.set_xlabel('시간 (초)')
            ax.set_ylabel('사용률 (%)')
            ax.grid(True, alpha=0.3)
            ax.set_ylim(0, 100)

            # 통계선 추가
            if 'cpu_percent' in self.stats:
                ax.axhline(y=self.stats['cpu_percent']['avg'],
                          color='green', linestyle='--', linewidth=1, label='평균')
                ax.axhline(y=self.stats['cpu_percent']['max'],
                          color='red', linestyle='--', linewidth=1, label='최대')
            ax.legend()

        # CPU 온도 그래프
        if self.data_history['cpu_temp'] and any(self.data_history['cpu_temp']):
            ax = axes[0, 1]
            ax.plot(timestamps, self.data_history['cpu_temp'],
                   color='#f59e0b', linewidth=1.5, label='Temperature')
            ax.fill_between(timestamps, self.data_history['cpu_temp'],
                           alpha=0.3, color='#f59e0b')
            ax.set_title('CPU 온도 (°C)', fontweight='bold')
            ax.set_xlabel('시간 (초)')
            ax.set_ylabel('온도 (°C)')
            ax.grid(True, alpha=0.3)
            ax.legend()
        else:
            ax = axes[0, 1]
            ax.text(0.5, 0.5, 'CPU 온도 데이터 없음', ha='center', va='center')
            ax.set_title('CPU 온도 (°C)', fontweight='bold')

        # 메모리 사용률 그래프
        if self.data_history['memory_percent']:
            ax = axes[1, 0]
            ax.plot(timestamps, self.data_history['memory_percent'],
                   color='#764ba2', linewidth=1.5, label='Memory')
            ax.fill_between(timestamps, self.data_history['memory_percent'],
                           alpha=0.3, color='#764ba2')
            ax.set_title('메모리 사용률 (%)', fontweight='bold')
            ax.set_xlabel('시간 (초)')
            ax.set_ylabel('사용률 (%)')
            ax.grid(True, alpha=0.3)
            ax.set_ylim(0, 100)

            if 'memory_percent' in self.stats:
                ax.axhline(y=self.stats['memory_percent']['avg'],
                          color='green', linestyle='--', linewidth=1, label='평균')
            ax.legend()

        # 메모리 사용량 (GB) 그래프
        if self.data_history['memory_used']:
            ax = axes[1, 1]
            ax.plot(timestamps, self.data_history['memory_used'],
                   color='#8b5cf6', linewidth=1.5, label='Used')
            ax.fill_between(timestamps, self.data_history['memory_used'],
                           alpha=0.3, color='#8b5cf6')
            ax.set_title('메모리 사용량 (GB)', fontweight='bold')
            ax.set_xlabel('시간 (초)')
            ax.set_ylabel('사용량 (GB)')
            ax.grid(True, alpha=0.3)
            ax.legend()

        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_gpu_disk_page(self, pdf):
        """GPU 및 디스크 페이지 생성"""
        fig, axes = plt.subplots(2, 2, figsize=(11, 8.5))
        fig.suptitle('GPU 및 디스크 모니터링', fontsize=16, fontweight='bold')

        timestamps = range(len(self.data_history['timestamps']))

        # GPU 사용률 그래프
        if self.data_history['gpu_usage'] and any(self.data_history['gpu_usage']):
            ax = axes[0, 0]
            ax.plot(timestamps, self.data_history['gpu_usage'],
                   color='#10b981', linewidth=1.5, label='GPU')
            ax.fill_between(timestamps, self.data_history['gpu_usage'],
                           alpha=0.3, color='#10b981')
            ax.set_title('GPU 사용률 (%)', fontweight='bold')
            ax.set_xlabel('시간 (초)')
            ax.set_ylabel('사용률 (%)')
            ax.grid(True, alpha=0.3)
            ax.set_ylim(0, 100)
            ax.legend()
        else:
            ax = axes[0, 0]
            ax.text(0.5, 0.5, 'GPU 데이터 없음', ha='center', va='center')
            ax.set_title('GPU 사용률 (%)', fontweight='bold')

        # GPU 온도 그래프
        if self.data_history['gpu_temp'] and any(self.data_history['gpu_temp']):
            ax = axes[0, 1]
            ax.plot(timestamps, self.data_history['gpu_temp'],
                   color='#ef4444', linewidth=1.5, label='GPU Temp')
            ax.fill_between(timestamps, self.data_history['gpu_temp'],
                           alpha=0.3, color='#ef4444')
            ax.set_title('GPU 온도 (°C)', fontweight='bold')
            ax.set_xlabel('시간 (초)')
            ax.set_ylabel('온도 (°C)')
            ax.grid(True, alpha=0.3)
            ax.legend()
        else:
            ax = axes[0, 1]
            ax.text(0.5, 0.5, 'GPU 온도 데이터 없음', ha='center', va='center')
            ax.set_title('GPU 온도 (°C)', fontweight='bold')

        # 디스크 사용률 그래프
        if self.data_history['disk_percent']:
            ax = axes[1, 0]
            ax.plot(timestamps, self.data_history['disk_percent'],
                   color='#f59e0b', linewidth=1.5, label='Disk')
            ax.fill_between(timestamps, self.data_history['disk_percent'],
                           alpha=0.3, color='#f59e0b')
            ax.set_title('디스크 사용률 (%)', fontweight='bold')
            ax.set_xlabel('시간 (초)')
            ax.set_ylabel('사용률 (%)')
            ax.grid(True, alpha=0.3)
            ax.set_ylim(0, 100)
            ax.legend()

        # 디스크 I/O 그래프
        if self.data_history['disk_read'] and self.data_history['disk_write']:
            ax = axes[1, 1]
            ax.plot(timestamps, self.data_history['disk_read'],
                   color='#3b82f6', linewidth=1.5, label='Read')
            ax.plot(timestamps, self.data_history['disk_write'],
                   color='#ef4444', linewidth=1.5, label='Write')
            ax.set_title('디스크 I/O 속도 (MB/s)', fontweight='bold')
            ax.set_xlabel('시간 (초)')
            ax.set_ylabel('속도 (MB/s)')
            ax.grid(True, alpha=0.3)
            ax.legend()

        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_network_page(self, pdf):
        """네트워크 페이지 생성"""
        fig, axes = plt.subplots(2, 1, figsize=(11, 8.5))
        fig.suptitle('네트워크 모니터링', fontsize=16, fontweight='bold')

        timestamps = range(len(self.data_history['timestamps']))

        # 네트워크 속도 그래프
        if self.data_history['network_recv'] and self.data_history['network_sent']:
            ax = axes[0]
            ax.plot(timestamps, self.data_history['network_recv'],
                   color='#3b82f6', linewidth=1.5, label='Download')
            ax.plot(timestamps, self.data_history['network_sent'],
                   color='#ef4444', linewidth=1.5, label='Upload')
            ax.fill_between(timestamps, self.data_history['network_recv'],
                           alpha=0.2, color='#3b82f6')
            ax.fill_between(timestamps, self.data_history['network_sent'],
                           alpha=0.2, color='#ef4444')
            ax.set_title('네트워크 전송 속도 (MB/s)', fontweight='bold')
            ax.set_xlabel('시간 (초)')
            ax.set_ylabel('속도 (MB/s)')
            ax.grid(True, alpha=0.3)
            ax.legend()

            # 통계 텍스트
            if self.data_history['network_recv']:
                avg_down = np.mean(self.data_history['network_recv'])
                max_down = np.max(self.data_history['network_recv'])
                avg_up = np.mean(self.data_history['network_sent'])
                max_up = np.max(self.data_history['network_sent'])

                stats_text = f"""
네트워크 통계:

다운로드:
  평균: {avg_down:.2f} MB/s
  최대: {max_down:.2f} MB/s

업로드:
  평균: {avg_up:.2f} MB/s
  최대: {max_up:.2f} MB/s
"""
                ax = axes[1]
                ax.text(0.5, 0.5, stats_text, ha='center', va='center',
                       fontsize=12, family='monospace',
                       bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
                ax.axis('off')

        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_statistics_page(self, pdf):
        """통계 요약 페이지 생성"""
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle('통계 요약', fontsize=16, fontweight='bold')

        stats_text = "모니터링 통계 요약\n\n"
        stats_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        # CPU 통계
        if 'cpu_percent' in self.stats:
            stats_text += f"CPU:\n"
            stats_text += f"  평균 사용률: {self.stats['cpu_percent']['avg']:.2f}%\n"
            stats_text += f"  최소 사용률: {self.stats['cpu_percent']['min']:.2f}%\n"
            stats_text += f"  최대 사용률: {self.stats['cpu_percent']['max']:.2f}%\n\n"

        if 'cpu_temp' in self.stats:
            stats_text += f"CPU 온도:\n"
            stats_text += f"  평균: {self.stats['cpu_temp']['avg']:.2f}°C\n"
            stats_text += f"  최소: {self.stats['cpu_temp']['min']:.2f}°C\n"
            stats_text += f"  최대: {self.stats['cpu_temp']['max']:.2f}°C\n\n"

        # 메모리 통계
        if 'memory_percent' in self.stats:
            stats_text += f"메모리:\n"
            stats_text += f"  평균 사용률: {self.stats['memory_percent']['avg']:.2f}%\n"
            stats_text += f"  최소 사용률: {self.stats['memory_percent']['min']:.2f}%\n"
            stats_text += f"  최대 사용률: {self.stats['memory_percent']['max']:.2f}%\n\n"

        # GPU 통계
        if 'gpu_usage' in self.stats:
            stats_text += f"GPU:\n"
            stats_text += f"  평균 사용률: {self.stats['gpu_usage']['avg']:.2f}%\n"
            stats_text += f"  최소 사용률: {self.stats['gpu_usage']['min']:.2f}%\n"
            stats_text += f"  최대 사용률: {self.stats['gpu_usage']['max']:.2f}%\n\n"

        # 디스크 통계
        if 'disk_percent' in self.stats:
            stats_text += f"디스크:\n"
            stats_text += f"  평균 사용률: {self.stats['disk_percent']['avg']:.2f}%\n"
            stats_text += f"  최소 사용률: {self.stats['disk_percent']['min']:.2f}%\n"
            stats_text += f"  최대 사용률: {self.stats['disk_percent']['max']:.2f}%\n\n"

        # 네트워크 통계
        if 'network_recv' in self.stats:
            stats_text += f"네트워크 다운로드:\n"
            stats_text += f"  평균: {self.stats['network_recv']['avg']:.2f} MB/s\n"
            stats_text += f"  최대: {self.stats['network_recv']['max']:.2f} MB/s\n\n"

        if 'network_sent' in self.stats:
            stats_text += f"네트워크 업로드:\n"
            stats_text += f"  평균: {self.stats['network_sent']['avg']:.2f} MB/s\n"
            stats_text += f"  최대: {self.stats['network_sent']['max']:.2f} MB/s\n\n"

        stats_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        stats_text += f"\n리포트 생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        plt.text(0.5, 0.5, stats_text, ha='center', va='center',
                fontsize=11, family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))

        plt.axis('off')
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
