// Socket.IO 연결
const socket = io();

// 차트 데이터 저장
const chartData = {
    cpu: { x: [], y: [] },
    memory: { x: [], y: [] },
    gpu: { x: [], y: [] },
    disk: { x: [], y: [] },
    network: { upload: [], download: [], x: [] }
};

// 통계 데이터
const stats = {
    cpu: { values: [], sum: 0, max: 0 },
    memory: { values: [], sum: 0, max: 0 },
    gpu: { values: [], sum: 0, max: 0 }
};

// 최대 데이터 포인트 수
const MAX_POINTS = 300; // 5분 = 300초

// 차트 레이아웃 설정
const commonLayout = {
    margin: { l: 50, r: 30, t: 10, b: 40 },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: 'Segoe UI', size: 12 },
    showlegend: true,
    legend: { orientation: 'h', y: -0.2 },
    xaxis: {
        showgrid: true,
        gridcolor: '#e0e0e0',
        zeroline: false
    },
    yaxis: {
        showgrid: true,
        gridcolor: '#e0e0e0',
        zeroline: false,
        range: [0, 100]
    }
};

const config = {
    responsive: true,
    displayModeBar: false
};

// 차트 초기화
function initCharts() {
    // CPU 차트
    Plotly.newPlot('cpuChart', [{
        x: [],
        y: [],
        type: 'scatter',
        mode: 'lines',
        name: 'CPU',
        line: { color: '#667eea', width: 2 },
        fill: 'tozeroy',
        fillcolor: 'rgba(102, 126, 234, 0.2)'
    }], {
        ...commonLayout,
        yaxis: { ...commonLayout.yaxis, title: 'Usage (%)' }
    }, config);

    // Memory 차트
    Plotly.newPlot('memChart', [{
        x: [],
        y: [],
        type: 'scatter',
        mode: 'lines',
        name: 'Memory',
        line: { color: '#764ba2', width: 2 },
        fill: 'tozeroy',
        fillcolor: 'rgba(118, 75, 162, 0.2)'
    }], {
        ...commonLayout,
        yaxis: { ...commonLayout.yaxis, title: 'Usage (%)' }
    }, config);

    // GPU 차트
    Plotly.newPlot('gpuChart', [{
        x: [],
        y: [],
        type: 'scatter',
        mode: 'lines',
        name: 'GPU',
        line: { color: '#10b981', width: 2 },
        fill: 'tozeroy',
        fillcolor: 'rgba(16, 185, 129, 0.2)'
    }], {
        ...commonLayout,
        yaxis: { ...commonLayout.yaxis, title: 'Usage (%)' }
    }, config);

    // Disk 차트
    Plotly.newPlot('diskChart', [{
        x: [],
        y: [],
        type: 'scatter',
        mode: 'lines',
        name: 'Disk',
        line: { color: '#f59e0b', width: 2 },
        fill: 'tozeroy',
        fillcolor: 'rgba(245, 158, 11, 0.2)'
    }], {
        ...commonLayout,
        yaxis: { ...commonLayout.yaxis, title: 'Usage (%)' }
    }, config);

    // Network 차트
    Plotly.newPlot('netChart', [
        {
            x: [],
            y: [],
            type: 'scatter',
            mode: 'lines',
            name: 'Download',
            line: { color: '#3b82f6', width: 2 }
        },
        {
            x: [],
            y: [],
            type: 'scatter',
            mode: 'lines',
            name: 'Upload',
            line: { color: '#ef4444', width: 2 }
        }
    ], {
        ...commonLayout,
        yaxis: { ...commonLayout.yaxis, title: 'Speed (MB/s)', range: null }
    }, config);
}

// 상태 클래스 가져오기
function getStatusClass(status) {
    switch(status) {
        case 'normal': return 'normal';
        case 'warning': return 'warning';
        case 'critical': return 'critical';
        default: return 'normal';
    }
}

function getStatusText(status) {
    switch(status) {
        case 'normal': return '정상';
        case 'warning': return '경고';
        case 'critical': return '위험';
        default: return '정상';
    }
}

// 데이터 업데이트
function updateData(data) {
    const timestamp = new Date().toLocaleTimeString();

    // CPU 업데이트
    if (data.cpu && !data.cpu.error) {
        chartData.cpu.x.push(timestamp);
        chartData.cpu.y.push(data.cpu.percent);

        // 통계 업데이트
        stats.cpu.values.push(data.cpu.percent);
        stats.cpu.sum += data.cpu.percent;
        stats.cpu.max = Math.max(stats.cpu.max, data.cpu.percent);

        // UI 업데이트
        document.getElementById('cpuCurrent').textContent = data.cpu.percent.toFixed(1) + '%';
        document.getElementById('cpuAvg').textContent = (stats.cpu.sum / stats.cpu.values.length).toFixed(1) + '%';
        document.getElementById('cpuMax').textContent = stats.cpu.max.toFixed(1) + '%';
        document.getElementById('cpuTemp').textContent = data.cpu.temperature.toFixed(1) + '°C';

        const cpuStatusBadge = document.getElementById('cpuStatus');
        cpuStatusBadge.className = 'status-badge ' + getStatusClass(data.cpu.status);
        cpuStatusBadge.textContent = getStatusText(data.cpu.status);

        updateChart('cpuChart', chartData.cpu.x, chartData.cpu.y);
    }

    // Memory 업데이트
    if (data.memory && !data.memory.error) {
        chartData.memory.x.push(timestamp);
        chartData.memory.y.push(data.memory.percent);

        stats.memory.values.push(data.memory.percent);
        stats.memory.sum += data.memory.percent;
        stats.memory.max = Math.max(stats.memory.max, data.memory.percent);

        document.getElementById('memCurrent').textContent = data.memory.percent.toFixed(1) + '%';
        document.getElementById('memUsed').textContent = data.memory.used.toFixed(2) + ' GB';
        document.getElementById('memAvail').textContent = data.memory.available.toFixed(2) + ' GB';

        const memStatusBadge = document.getElementById('memStatus');
        memStatusBadge.className = 'status-badge ' + getStatusClass(data.memory.status);
        memStatusBadge.textContent = getStatusText(data.memory.status);

        updateChart('memChart', chartData.memory.x, chartData.memory.y);
    }

    // GPU 업데이트
    if (data.gpu && data.gpu.length > 0 && !data.gpu[0].error) {
        const gpu = data.gpu[0];
        chartData.gpu.x.push(timestamp);
        chartData.gpu.y.push(gpu.load);

        stats.gpu.values.push(gpu.load);
        stats.gpu.sum += gpu.load;
        stats.gpu.max = Math.max(stats.gpu.max, gpu.load);

        document.getElementById('gpuCurrent').textContent = gpu.load.toFixed(1) + '%';
        document.getElementById('gpuTemp').textContent = gpu.temperature.toFixed(1) + '°C';
        document.getElementById('gpuMem').textContent = gpu.memory_used.toFixed(0) + ' / ' + gpu.memory_total.toFixed(0) + ' MB';

        const gpuStatusBadge = document.getElementById('gpuStatus');
        gpuStatusBadge.className = 'status-badge ' + getStatusClass(gpu.status);
        gpuStatusBadge.textContent = getStatusText(gpu.status);

        updateChart('gpuChart', chartData.gpu.x, chartData.gpu.y);
    } else {
        document.getElementById('gpuCurrent').textContent = 'N/A';
        document.getElementById('gpuTemp').textContent = 'N/A';
        document.getElementById('gpuMem').textContent = 'N/A';
    }

    // Disk 업데이트
    if (data.disk && !data.disk.error) {
        chartData.disk.x.push(timestamp);
        chartData.disk.y.push(data.disk.percent);

        document.getElementById('diskCurrent').textContent = data.disk.percent.toFixed(1) + '%';
        document.getElementById('diskRead').textContent = data.disk.read_speed.toFixed(2) + ' MB/s';
        document.getElementById('diskWrite').textContent = data.disk.write_speed.toFixed(2) + ' MB/s';

        const diskStatusBadge = document.getElementById('diskStatus');
        diskStatusBadge.className = 'status-badge ' + getStatusClass(data.disk.status);
        diskStatusBadge.textContent = getStatusText(data.disk.status);

        updateChart('diskChart', chartData.disk.x, chartData.disk.y);
    }

    // Network 업데이트
    if (data.network && !data.network.error) {
        chartData.network.x.push(timestamp);
        chartData.network.download.push(data.network.download_speed);
        chartData.network.upload.push(data.network.upload_speed);

        document.getElementById('netDown').textContent = data.network.download_speed.toFixed(2) + ' MB/s';
        document.getElementById('netUp').textContent = data.network.upload_speed.toFixed(2) + ' MB/s';

        updateNetworkChart(chartData.network.x, chartData.network.download, chartData.network.upload);
    }

    // Processes 업데이트
    if (data.processes && data.processes.length > 0) {
        updateProcessTable(data.processes);
    }

    // 데이터 포인트 제한
    limitDataPoints();
}

// 차트 업데이트 (단일 라인)
function updateChart(chartId, x, y) {
    Plotly.update(chartId, {
        x: [x],
        y: [y]
    }, {}, [0]);
}

// 네트워크 차트 업데이트 (두 라인)
function updateNetworkChart(x, download, upload) {
    Plotly.update('netChart', {
        x: [x, x],
        y: [download, upload]
    }, {}, [0, 1]);
}

// 프로세스 테이블 업데이트
function updateProcessTable(processes) {
    const tbody = document.getElementById('processTable');
    tbody.innerHTML = '';

    processes.forEach(proc => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${proc.pid}</td>
            <td>${proc.name}</td>
            <td>${proc.cpu_percent.toFixed(1)}%</td>
            <td>${proc.memory_percent.toFixed(1)}%</td>
        `;
    });
}

// 데이터 포인트 제한
function limitDataPoints() {
    for (let key in chartData) {
        if (key === 'network') {
            if (chartData[key].x.length > MAX_POINTS) {
                chartData[key].x.shift();
                chartData[key].download.shift();
                chartData[key].upload.shift();
            }
        } else {
            if (chartData[key].x.length > MAX_POINTS) {
                chartData[key].x.shift();
                chartData[key].y.shift();
            }
        }
    }
}

// 시간 업데이트
function updateTime(duration, remaining) {
    document.getElementById('duration').textContent = duration;
    document.getElementById('remaining').textContent = remaining;
}

// Socket 이벤트 리스너
socket.on('connect', function() {
    console.log('서버에 연결되었습니다.');
});

socket.on('system_data', function(data) {
    updateData(data);
});

socket.on('time_update', function(data) {
    updateTime(data.duration, data.remaining);
});

socket.on('monitoring_complete', function(data) {
    document.getElementById('monitorStatus').textContent = '완료';
    document.getElementById('monitorStatus').className = 'status-badge normal';
    document.getElementById('footerMessage').textContent = data.message;

    if (data.pdf_path) {
        document.getElementById('footerMessage').innerHTML =
            `모니터링 완료! PDF 리포트가 생성되었습니다: <strong>${data.pdf_path}</strong>`;
    }
});

socket.on('disconnect', function() {
    console.log('서버와의 연결이 끊어졌습니다.');
});

// 페이지 로드 시 차트 초기화
window.addEventListener('DOMContentLoaded', function() {
    initCharts();
    console.log('대시보드 초기화 완료');
});
