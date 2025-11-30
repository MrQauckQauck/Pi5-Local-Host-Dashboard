class DashboardManager {
    constructor() {
        this.updateInterval = 2000; // Update every 2 seconds
        this.isUpdating = false;
        this.previousData = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.fetchAllMetrics();
        setInterval(() => this.fetchAllMetrics(), this.updateInterval);
    }

    setupEventListeners() {
        // Reboot button
        document.getElementById('reboot-btn').addEventListener('click', () => {
            if (confirm('Are you sure you want to reboot the system?')) {
                this.rebootSystem();
            }
        });

        // Shutdown button
        document.getElementById('shutdown-btn').addEventListener('click', () => {
            this.showShutdownModal();
        });

        // Shutdown modal controls
        document.getElementById('shutdown-cancel').addEventListener('click', () => {
            this.hideShutdownModal();
        });

        document.getElementById('shutdown-confirm').addEventListener('click', () => {
            this.confirmShutdown();
        });

        // Close modal when clicking outside
        document.getElementById('shutdown-modal').addEventListener('click', (e) => {
            if (e.target.id === 'shutdown-modal') {
                this.hideShutdownModal();
            }
        });

        // Allow Enter key to confirm shutdown
        document.getElementById('shutdown-password').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.confirmShutdown();
            }
        });
    }

    async fetchAllMetrics() {
        if (this.isUpdating) return;
        this.isUpdating = true;

        try {
            const response = await fetch('/api/metrics/all');
            const data = await response.json();
            
            if (data) {
                this.previousData = data;
                this.updateDashboard(data);
                this.updateLastUpdateTime();
            }
        } catch (error) {
            console.error('Error fetching metrics:', error);
        } finally {
            this.isUpdating = false;
        }
    }

    updateDashboard(data) {
        if (data.system_info) this.updateSystemInfo(data.system_info);
        if (data.cpu) this.updateCPUMetrics(data.cpu);
        if (data.memory) this.updateMemoryMetrics(data.memory);
        if (data.storage) this.updateStorageMetrics(data.storage);
    }

    updateSystemInfo(info) {
        document.getElementById('hostname').textContent = info.hostname;
        document.getElementById('info-system').textContent = info.system;
        document.getElementById('info-release').textContent = info.release;
        document.getElementById('info-machine').textContent = info.machine;
        document.getElementById('info-boot-time').textContent = new Date(info.boot_time).toLocaleString();
        
        const uptimeSeconds = info.uptime_seconds;
        const uptime = this.formatUptime(uptimeSeconds);
        document.getElementById('uptime').textContent = `Uptime: ${uptime}`;
        
        // Network info
        if (info.network) {
            document.getElementById('ip-address').textContent = `IP: ${info.network.ip_address}`;
            document.getElementById('gateway').textContent = `GW: ${info.network.gateway}`;
            document.getElementById('dns').textContent = `DNS: ${info.network.dns}`;
        }
    }

    formatUptime(seconds) {
        const days = Math.floor(seconds / 86400);
        const hours = Math.floor((seconds % 86400) / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        
        const parts = [];
        if (days > 0) parts.push(`${days}d`);
        if (hours > 0) parts.push(`${hours}h`);
        if (minutes > 0) parts.push(`${minutes}m`);
        
        return parts.length > 0 ? parts.join(' ') : 'just now';
    }

    celsiusToFahrenheit(celsius) {
        return (celsius * 9/5) + 32;
    }

    updateCPUMetrics(cpu) {
        // Temperature
        if (cpu.temperature !== null) {
            const tempC = cpu.temperature;
            const tempF = this.celsiusToFahrenheit(tempC);
            document.getElementById('temp-value').textContent = tempF.toFixed(1);
            
            const tempPercent = Math.min((tempC / 85) * 100, 100);
            const gauge = document.getElementById('temp-gauge-fill');
            gauge.style.strokeDasharray = `${tempPercent * 5.65} ${565}`;
            
            const badge = document.getElementById('temp-status');
            if (tempC > 75) {
                badge.textContent = 'Hot';
                badge.className = 'status-badge error';
                gauge.style.stroke = 'var(--error-color)';
            } else if (tempC > 60) {
                badge.textContent = 'Warm';
                badge.className = 'status-badge warning';
                gauge.style.stroke = 'var(--warning-color)';
            } else {
                badge.textContent = 'Normal';
                badge.className = 'status-badge';
                gauge.style.stroke = 'var(--success-color)';
            }
        }

        // CPU Usage
        const avgUsage = cpu.average_usage;
        document.getElementById('cpu-usage-percent').textContent = avgUsage.toFixed(1) + '%';
        document.getElementById('cpu-cores-info').textContent = `${cpu.logical_cores} cores`;
        
        const cpuFill = document.getElementById('cpu-usage-fill');
        cpuFill.style.width = avgUsage + '%';
        if (avgUsage > 80) {
            cpuFill.classList.add('error');
            cpuFill.classList.remove('warning');
        } else if (avgUsage > 60) {
            cpuFill.classList.add('warning');
            cpuFill.classList.remove('error');
        } else {
            cpuFill.classList.remove('error', 'warning');
        }

        // Per-core usage
        this.updateCoresDisplay(cpu.per_core_usage);

        // Frequency
        if (cpu.current_freq) {
            document.getElementById('cpu-freq-current').textContent = 
                cpu.current_freq.toFixed(0) + ' MHz';
            document.getElementById('cpu-freq-range').textContent = 
                `${cpu.min_freq.toFixed(0)} / ${cpu.max_freq.toFixed(0)} MHz`;
        }

        // Voltage
        if (cpu.voltage !== null) {
            document.getElementById('cpu-voltage').textContent = 
                cpu.voltage.toFixed(3) + ' V';
        }

        // Throttling
        this.updateThrottlingStatus(cpu.throttling);
    }

    updateCoresDisplay(perCoreUsage) {
        const container = document.getElementById('cores-container');
        container.innerHTML = '';

        perCoreUsage.forEach((usage, index) => {
            const coreItem = document.createElement('div');
            coreItem.className = 'core-item';
            
            const color = usage > 80 ? '#F44336' : usage > 60 ? '#FF9800' : '#2196F3';
            
            coreItem.innerHTML = `
                <div class="core-label">Core ${index}</div>
                <div class="core-usage" style="color: ${color}">${usage.toFixed(0)}%</div>
            `;
            
            container.appendChild(coreItem);
        });
    }

    updateThrottlingStatus(throttling) {
        const container = document.getElementById('throttling-status');
        container.innerHTML = '';

        const items = [
            { key: 'under_voltage', label: 'Under Voltage' },
            { key: 'arm_freq_capped', label: 'Freq Capped' },
            { key: 'soft_temp_limit', label: 'Temp Limit' },
            { key: 'throttling_now', label: 'Throttling Now' }
        ];

        items.forEach(item => {
            const div = document.createElement('div');
            div.className = 'throttle-item';
            
            if (throttling[item.key]) {
                div.classList.add('error');
                div.innerHTML = `
                    <div class="throttle-item-label">⚠️ ${item.label}</div>
                    <div class="throttle-item-value">ACTIVE</div>
                `;
            } else {
                div.innerHTML = `
                    <div class="throttle-item-label">✓ ${item.label}</div>
                    <div class="throttle-item-value">Normal</div>
                `;
            }
            
            container.appendChild(div);
        });
    }

    updateMemoryMetrics(memory) {
        // RAM
        const ramPercent = memory.ram_percent;
        document.getElementById('ram-usage-fill').style.width = ramPercent + '%';
        document.getElementById('ram-used').textContent = this.formatBytes(memory.ram_used);
        document.getElementById('ram-total').textContent = this.formatBytes(memory.ram_total);
        document.getElementById('ram-available').textContent = this.formatBytes(memory.ram_available);
        document.getElementById('ram-cached').textContent = this.formatBytes(memory.ram_cached);

        const ramFill = document.getElementById('ram-usage-fill');
        if (ramPercent > 80) {
            ramFill.classList.add('error');
            ramFill.classList.remove('warning');
        } else if (ramPercent > 60) {
            ramFill.classList.add('warning');
            ramFill.classList.remove('error');
        } else {
            ramFill.classList.remove('error', 'warning');
        }

        // Swap
        const swapPercent = memory.swap_percent;
        document.getElementById('swap-usage-fill').style.width = swapPercent + '%';
        document.getElementById('swap-used').textContent = this.formatBytes(memory.swap_used);
        document.getElementById('swap-total').textContent = this.formatBytes(memory.swap_total);
        document.getElementById('swap-free').textContent = this.formatBytes(memory.swap_free);

        const swapFill = document.getElementById('swap-usage-fill');
        if (swapPercent > 50) {
            swapFill.classList.add('error');
            swapFill.classList.remove('warning');
        } else if (swapPercent > 25) {
            swapFill.classList.add('warning');
            swapFill.classList.remove('error');
        } else {
            swapFill.classList.remove('error', 'warning');
        }

        // Excessive swap alert
        const alert = document.getElementById('excessive-swap-alert');
        if (memory.excessive_swap) {
            alert.textContent = '⚠️ Excessive swapping detected - RAM may be insufficient for current workload';
            alert.classList.remove('alert-hidden');
        } else {
            alert.classList.add('alert-hidden');
        }
    }

    updateStorageMetrics(storage) {
        const container = document.getElementById('partitions-container');
        container.innerHTML = '';

        storage.partitions.forEach(partition => {
            const percent = partition.percent;
            const item = document.createElement('div');
            item.className = 'partition-item';

            const fillColor = percent > 80 ? '#F44336' : percent > 60 ? '#FF9800' : '#2196F3';

            item.innerHTML = `
                <div class="partition-header">
                    <span class="partition-name">${partition.device}</span>
                    <span class="partition-percent">${percent.toFixed(1)}%</span>
                </div>
                <div class="partition-type">${partition.fstype} @ ${partition.mountpoint}</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${percent}%; background-color: ${fillColor}"></div>
                </div>
                <div class="partition-details">
                    <span>Free: ${this.formatBytes(partition.free)}</span>
                    <span>Used: ${this.formatBytes(partition.used)}</span>
                    <span>Total: ${this.formatBytes(partition.total)}</span>
                </div>
            `;

            container.appendChild(item);
        });

        // I/O Counters
        if (storage.io_counters) {
            const io = storage.io_counters;
            document.getElementById('io-read-count').textContent = 
                this.formatNumber(io.read_count) + ' ops';
            document.getElementById('io-read-data').textContent = 
                this.formatBytes(io.read_bytes);
            document.getElementById('io-write-count').textContent = 
                this.formatNumber(io.write_count) + ' ops';
            document.getElementById('io-write-data').textContent = 
                this.formatBytes(io.write_bytes);
            document.getElementById('io-read-time').textContent = 
                io.read_time + ' ms';
            document.getElementById('io-write-time').textContent = 
                io.write_time + ' ms';
        }
    }

    updateSmartData(smart) {
        const container = document.getElementById('smart-container');
        container.innerHTML = '';

        if (!smart.available) {
            container.innerHTML = '<div class="smart-status">S.M.A.R.T data not available (smartctl not installed)</div>';
            return;
        }

        if (smart.devices.length === 0) {
            container.innerHTML = '<div class="smart-status">No S.M.A.R.T devices detected</div>';
            return;
        }

        smart.devices.forEach(device => {
            const healthClass = device.health.toLowerCase();
            const deviceDiv = document.createElement('div');
            deviceDiv.className = 'smart-device';

            let details = '';
            if (device.temperature !== null) {
                const tempF = this.celsiusToFahrenheit(device.temperature);
                details += `<div class="smart-detail-item">
                    <div class="smart-detail-label">Temperature</div>
                    <div class="smart-detail-value">${tempF.toFixed(0)}°F</div>
                </div>`;
            }
            if (device.power_on_hours !== null) {
                details += `<div class="smart-detail-item">
                    <div class="smart-detail-label">Power-On Hours</div>
                    <div class="smart-detail-value">${this.formatNumber(device.power_on_hours)}</div>
                </div>`;
            }
            if (device.raw_read_error_rate !== null) {
                details += `<div class="smart-detail-item">
                    <div class="smart-detail-label">Read Errors</div>
                    <div class="smart-detail-value">${device.raw_read_error_rate}</div>
                </div>`;
            }
            if (device.reallocated_sector_count !== null) {
                details += `<div class="smart-detail-item">
                    <div class="smart-detail-label">Bad Sectors</div>
                    <div class="smart-detail-value">${device.reallocated_sector_count}</div>
                </div>`;
            }

            deviceDiv.innerHTML = `
                <div class="smart-device-header">
                    <span class="smart-device-name">${device.device}</span>
                    <span class="smart-health ${healthClass}">${device.health}</span>
                </div>
                <div class="smart-details">
                    ${details}
                </div>
            `;

            container.appendChild(deviceDiv);
        });
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return (bytes / Math.pow(k, i)).toFixed(1) + ' ' + sizes[i];
    }

    formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }

    updateLastUpdateTime() {
        const now = new Date();
        const timeStr = now.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit',
            hour12: true 
        });
        document.getElementById('last-update').textContent = `Last update: ${timeStr}`;
    }

    showShutdownModal() {
        document.getElementById('shutdown-modal').classList.remove('modal-hidden');
        document.getElementById('shutdown-password').focus();
    }

    hideShutdownModal() {
        document.getElementById('shutdown-modal').classList.add('modal-hidden');
        document.getElementById('shutdown-password').value = '';
    }

    async rebootSystem() {
        try {
            const response = await fetch('/api/system/reboot', { method: 'POST' });
            const data = await response.json();
            if (data.status === 'success') {
                alert('System is rebooting...');
            } else {
                alert('Error: ' + data.message);
            }
        } catch (error) {
            alert('Failed to send reboot command: ' + error);
        }
    }

    async confirmShutdown() {
        const password = document.getElementById('shutdown-password').value;
        
        if (!password) {
            alert('Please enter the password');
            return;
        }

        try {
            const response = await fetch('/api/system/shutdown', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ password: password })
            });

            const data = await response.json();
            
            if (response.status === 401) {
                alert('Incorrect password');
                document.getElementById('shutdown-password').value = '';
                document.getElementById('shutdown-password').focus();
                return;
            }

            if (data.status === 'success') {
                alert('System is shutting down...');
                this.hideShutdownModal();
            } else {
                alert('Error: ' + data.message);
            }
        } catch (error) {
            alert('Failed to send shutdown command: ' + error);
        }
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new DashboardManager();
});
