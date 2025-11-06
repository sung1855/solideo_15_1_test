"""
System Resource Monitor
실시간 시스템 리소스 모니터링 모듈
"""

import psutil
import platform
import time
from datetime import datetime
from typing import Dict, List, Any
import GPUtil

class SystemMonitor:
    """시스템 리소스를 모니터링하는 클래스"""

    def __init__(self):
        self.data_history = {
            'timestamps': [],
            'cpu_percent': [],
            'cpu_per_core': [],
            'cpu_temp': [],
            'memory_percent': [],
            'memory_used': [],
            'disk_percent': [],
            'disk_read': [],
            'disk_write': [],
            'network_sent': [],
            'network_recv': [],
            'gpu_usage': [],
            'gpu_temp': [],
            'top_processes': []
        }
        self.start_time = None
        self.net_io_last = None
        self.disk_io_last = None

    def get_system_info(self) -> Dict[str, Any]:
        """시스템 기본 정보 수집"""
        try:
            cpu_freq = psutil.cpu_freq()
            mem = psutil.virtual_memory()

            return {
                'os': f"{platform.system()} {platform.release()}",
                'os_version': platform.version(),
                'architecture': platform.machine(),
                'processor': platform.processor(),
                'cpu_count': psutil.cpu_count(logical=False),
                'cpu_threads': psutil.cpu_count(logical=True),
                'cpu_freq_max': f"{cpu_freq.max:.2f} MHz" if cpu_freq else "N/A",
                'total_memory': f"{mem.total / (1024**3):.2f} GB",
                'hostname': platform.node()
            }
        except Exception as e:
            return {'error': str(e)}

    def get_cpu_info(self) -> Dict[str, Any]:
        """CPU 정보 수집"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_per_core = psutil.cpu_percent(interval=0.1, percpu=True)
            cpu_freq = psutil.cpu_freq()

            # CPU 온도 (Linux의 경우)
            cpu_temp = self._get_cpu_temperature()

            return {
                'percent': cpu_percent,
                'per_core': cpu_per_core,
                'frequency': cpu_freq.current if cpu_freq else 0,
                'temperature': cpu_temp,
                'status': self._get_status(cpu_percent)
            }
        except Exception as e:
            return {'error': str(e)}

    def _get_cpu_temperature(self) -> float:
        """CPU 온도 가져오기"""
        try:
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    # 다양한 센서 이름 시도
                    for name in ['coretemp', 'cpu_thermal', 'k10temp', 'zenpower']:
                        if name in temps:
                            return temps[name][0].current
                    # 첫 번째 센서 사용
                    if temps:
                        first_sensor = list(temps.values())[0]
                        if first_sensor:
                            return first_sensor[0].current
        except:
            pass
        return 0.0

    def get_memory_info(self) -> Dict[str, Any]:
        """메모리 정보 수집"""
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()

            return {
                'percent': mem.percent,
                'used': mem.used / (1024**3),  # GB
                'available': mem.available / (1024**3),  # GB
                'total': mem.total / (1024**3),  # GB
                'swap_percent': swap.percent,
                'swap_used': swap.used / (1024**3),  # GB
                'status': self._get_status(mem.percent)
            }
        except Exception as e:
            return {'error': str(e)}

    def get_disk_info(self) -> Dict[str, Any]:
        """디스크 정보 수집"""
        try:
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()

            # I/O 속도 계산
            read_speed = 0
            write_speed = 0
            if self.disk_io_last:
                time_delta = time.time() - self.disk_io_last['time']
                if time_delta > 0:
                    read_speed = (disk_io.read_bytes - self.disk_io_last['read']) / time_delta / (1024**2)  # MB/s
                    write_speed = (disk_io.write_bytes - self.disk_io_last['write']) / time_delta / (1024**2)  # MB/s

            self.disk_io_last = {
                'time': time.time(),
                'read': disk_io.read_bytes,
                'write': disk_io.write_bytes
            }

            return {
                'percent': disk.percent,
                'used': disk.used / (1024**3),  # GB
                'free': disk.free / (1024**3),  # GB
                'total': disk.total / (1024**3),  # GB
                'read_speed': read_speed,
                'write_speed': write_speed,
                'status': self._get_status(disk.percent)
            }
        except Exception as e:
            return {'error': str(e)}

    def get_network_info(self) -> Dict[str, Any]:
        """네트워크 정보 수집"""
        try:
            net_io = psutil.net_io_counters()

            # 네트워크 속도 계산
            upload_speed = 0
            download_speed = 0
            if self.net_io_last:
                time_delta = time.time() - self.net_io_last['time']
                if time_delta > 0:
                    upload_speed = (net_io.bytes_sent - self.net_io_last['sent']) / time_delta / (1024**2)  # MB/s
                    download_speed = (net_io.bytes_recv - self.net_io_last['recv']) / time_delta / (1024**2)  # MB/s

            self.net_io_last = {
                'time': time.time(),
                'sent': net_io.bytes_sent,
                'recv': net_io.bytes_recv
            }

            return {
                'bytes_sent': net_io.bytes_sent / (1024**3),  # GB
                'bytes_recv': net_io.bytes_recv / (1024**3),  # GB
                'upload_speed': upload_speed,
                'download_speed': download_speed,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            }
        except Exception as e:
            return {'error': str(e)}

    def get_gpu_info(self) -> List[Dict[str, Any]]:
        """GPU 정보 수집"""
        try:
            gpus = GPUtil.getGPUs()
            gpu_list = []
            for gpu in gpus:
                gpu_list.append({
                    'id': gpu.id,
                    'name': gpu.name,
                    'load': gpu.load * 100,  # 퍼센트로 변환
                    'temperature': gpu.temperature,
                    'memory_used': gpu.memoryUsed,  # MB
                    'memory_total': gpu.memoryTotal,  # MB
                    'memory_percent': (gpu.memoryUsed / gpu.memoryTotal * 100) if gpu.memoryTotal > 0 else 0,
                    'status': self._get_status(gpu.load * 100)
                })
            return gpu_list
        except Exception as e:
            return [{'error': str(e)}]

    def get_top_processes(self, limit: int = 5) -> List[Dict[str, Any]]:
        """상위 프로세스 정보 수집"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    processes.append({
                        'pid': pinfo['pid'],
                        'name': pinfo['name'],
                        'cpu_percent': pinfo['cpu_percent'] or 0,
                        'memory_percent': pinfo['memory_percent'] or 0
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # CPU 사용률 기준으로 정렬
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            return processes[:limit]
        except Exception as e:
            return [{'error': str(e)}]

    def _get_status(self, percent: float) -> str:
        """상태 평가 (정상/경고/위험)"""
        if percent < 60:
            return 'normal'
        elif percent < 80:
            return 'warning'
        else:
            return 'critical'

    def collect_all_data(self) -> Dict[str, Any]:
        """모든 시스템 데이터 수집"""
        timestamp = datetime.now()

        data = {
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'disk': self.get_disk_info(),
            'network': self.get_network_info(),
            'gpu': self.get_gpu_info(),
            'processes': self.get_top_processes()
        }

        # 히스토리에 저장
        self._add_to_history(data)

        return data

    def _add_to_history(self, data: Dict[str, Any]):
        """데이터 히스토리에 추가"""
        self.data_history['timestamps'].append(data['timestamp'])

        # CPU
        if 'error' not in data['cpu']:
            self.data_history['cpu_percent'].append(data['cpu']['percent'])
            self.data_history['cpu_per_core'].append(data['cpu']['per_core'])
            self.data_history['cpu_temp'].append(data['cpu']['temperature'])

        # Memory
        if 'error' not in data['memory']:
            self.data_history['memory_percent'].append(data['memory']['percent'])
            self.data_history['memory_used'].append(data['memory']['used'])

        # Disk
        if 'error' not in data['disk']:
            self.data_history['disk_percent'].append(data['disk']['percent'])
            self.data_history['disk_read'].append(data['disk']['read_speed'])
            self.data_history['disk_write'].append(data['disk']['write_speed'])

        # Network
        if 'error' not in data['network']:
            self.data_history['network_sent'].append(data['network']['upload_speed'])
            self.data_history['network_recv'].append(data['network']['download_speed'])

        # GPU
        if data['gpu'] and 'error' not in data['gpu'][0]:
            gpu_loads = [gpu['load'] for gpu in data['gpu']]
            gpu_temps = [gpu['temperature'] for gpu in data['gpu']]
            self.data_history['gpu_usage'].append(gpu_loads[0] if gpu_loads else 0)
            self.data_history['gpu_temp'].append(gpu_temps[0] if gpu_temps else 0)

        # Processes
        self.data_history['top_processes'].append(data['processes'])

    def get_statistics(self) -> Dict[str, Any]:
        """통계 정보 계산"""
        stats = {}

        for key, values in self.data_history.items():
            if key in ['timestamps', 'cpu_per_core', 'top_processes']:
                continue

            if values and len(values) > 0:
                # GPU는 리스트일 수 있음
                if isinstance(values[0], list):
                    flat_values = [v for sublist in values for v in sublist if isinstance(v, (int, float))]
                    if flat_values:
                        stats[key] = {
                            'avg': sum(flat_values) / len(flat_values),
                            'min': min(flat_values),
                            'max': max(flat_values)
                        }
                else:
                    numeric_values = [v for v in values if isinstance(v, (int, float))]
                    if numeric_values:
                        stats[key] = {
                            'avg': sum(numeric_values) / len(numeric_values),
                            'min': min(numeric_values),
                            'max': max(numeric_values)
                        }

        return stats

    def start_monitoring(self):
        """모니터링 시작"""
        self.start_time = datetime.now()

    def get_monitoring_duration(self) -> str:
        """모니터링 기간 반환"""
        if self.start_time:
            duration = datetime.now() - self.start_time
            return str(duration).split('.')[0]  # 마이크로초 제거
        return "0:00:00"
