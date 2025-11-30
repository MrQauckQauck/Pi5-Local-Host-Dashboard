import psutil
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
import re

class SystemMonitor:
    """Comprehensive system monitoring for Raspberry Pi"""
    
    @staticmethod
    def get_cpu_metrics():
        """Get detailed CPU metrics including temperature, cores, and throttling"""
        metrics = {}
        
        # CPU count and frequency
        metrics['cores'] = psutil.cpu_count(logical=False) or 1
        metrics['logical_cores'] = psutil.cpu_count(logical=True) or 1
        
        # Per-core usage
        per_core_usage = psutil.cpu_percent(interval=1, percpu=True)
        metrics['per_core_usage'] = per_core_usage
        metrics['average_usage'] = sum(per_core_usage) / len(per_core_usage)
        
        # CPU frequencies
        freq = psutil.cpu_freq()
        metrics['current_freq'] = freq.current if freq else 0
        metrics['min_freq'] = freq.min if freq else 0
        metrics['max_freq'] = freq.max if freq else 0
        
        # Temperature (Raspberry Pi specific)
        metrics['temperature'] = SystemMonitor._get_cpu_temperature()
        
        # Throttling info (for RPi)
        metrics['throttling'] = SystemMonitor._get_throttling_info()
        
        # Voltage (for RPi)
        metrics['voltage'] = SystemMonitor._get_cpu_voltage()
        
        metrics['timestamp'] = datetime.now().isoformat()
        return metrics
    
    @staticmethod
    def _get_cpu_temperature():
        """Get CPU temperature from /sys/class/thermal or vcgencmd"""
        try:
            # Try reading from thermal zone first
            thermal_file = Path('/sys/class/thermal/thermal_zone0/temp')
            if thermal_file.exists():
                with open(thermal_file) as f:
                    temp_millidegrees = int(f.read().strip())
                    return temp_millidegrees / 1000
        except Exception:
            pass
        
        try:
            # Try vcgencmd for RPi
            result = subprocess.run(['vcgencmd', 'measure_temp'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                match = re.search(r"temp=([0-9.]+)'C", result.stdout)
                if match:
                    return float(match.group(1))
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def _get_throttling_info():
        """Get throttling status from Raspberry Pi"""
        try:
            result = subprocess.run(['vcgencmd', 'get_throttled'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                match = re.search(r'throttled=0x([0-9a-f]+)', result.stdout)
                if match:
                    throttled = int(match.group(1), 16)
                    return {
                        'throttling': bool(throttled & 0x1),
                        'arm_freq_capped': bool(throttled & 0x2),
                        'currently_throttled': bool(throttled & 0x4),
                        'soft_temp_limit': bool(throttled & 0x8),
                        'under_voltage': bool(throttled & 0x10),
                        'arm_freq_capped_now': bool(throttled & 0x20),
                        'throttling_now': bool(throttled & 0x40),
                        'soft_temp_limit_now': bool(throttled & 0x80),
                        'under_voltage_now': bool(throttled & 0x100),
                    }
        except Exception:
            pass
        
        return {
            'throttling': False,
            'arm_freq_capped': False,
            'currently_throttled': False,
            'soft_temp_limit': False,
            'under_voltage': False,
            'arm_freq_capped_now': False,
            'throttling_now': False,
            'soft_temp_limit_now': False,
            'under_voltage_now': False,
        }
    
    @staticmethod
    def _get_cpu_voltage():
        """Get CPU voltage from Raspberry Pi"""
        try:
            # Use /usr/bin/vcgencmd with full path to ensure PATH is correct
            result = subprocess.run(['/usr/bin/vcgencmd', 'measure_volts'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                match = re.search(r'volt=([0-9.]+)V', result.stdout)
                if match:
                    return float(match.group(1))
        except Exception as e:
            pass
        
        return None
    
    @staticmethod
    def get_memory_metrics():
        """Get detailed memory and swap metrics"""
        metrics = {}
        
        # RAM metrics
        virtual_memory = psutil.virtual_memory()
        metrics['ram_total'] = virtual_memory.total
        metrics['ram_used'] = virtual_memory.used
        metrics['ram_available'] = virtual_memory.available
        metrics['ram_percent'] = virtual_memory.percent
        metrics['ram_free'] = virtual_memory.free
        metrics['ram_buffers'] = virtual_memory.buffers
        metrics['ram_cached'] = virtual_memory.cached
        
        # Swap metrics
        swap_memory = psutil.swap_memory()
        metrics['swap_total'] = swap_memory.total
        metrics['swap_used'] = swap_memory.used
        metrics['swap_free'] = swap_memory.free
        metrics['swap_percent'] = swap_memory.percent
        
        # Excessive swapping detection
        metrics['excessive_swap'] = swap_memory.percent > 50 if swap_memory.total > 0 else False
        
        metrics['timestamp'] = datetime.now().isoformat()
        return metrics
    
    @staticmethod
    def get_storage_metrics():
        """Get storage metrics including disk space and I/O performance"""
        metrics = {
            'partitions': [],
            'io_counters': None,
            'timestamp': datetime.now().isoformat()
        }
        
        # Disk partitions
        for partition in psutil.disk_partitions():
            if partition.fstype:  # Skip virtual filesystems
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    metrics['partitions'].append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent,
                    })
                except PermissionError:
                    pass
        
        # I/O counters
        try:
            io_counters = psutil.disk_io_counters()
            metrics['io_counters'] = {
                'read_count': io_counters.read_count,
                'write_count': io_counters.write_count,
                'read_bytes': io_counters.read_bytes,
                'write_bytes': io_counters.write_bytes,
                'read_time': io_counters.read_time,
                'write_time': io_counters.write_time,
            }
        except Exception:
            pass
        
        return metrics
    
    @staticmethod
    def get_smart_data():
        """Get S.M.A.R.T data if available"""
        smart_data = {
            'available': False,
            'devices': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Check if smartctl is available
            result = subprocess.run(['which', 'smartctl'], 
                                  capture_output=True, timeout=2)
            if result.returncode != 0:
                return smart_data
            
            smart_data['available'] = True
            
            # Scan for smart devices
            result = subprocess.run(['smartctl', '--scan'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 or result.returncode == 1:
                for line in result.stdout.split('\n'):
                    if line.startswith('/dev/'):
                        device = line.split()[0]
                        smart_data['devices'].append(SystemMonitor._get_smart_device_info(device))
        except Exception:
            pass
        
        return smart_data
    
    @staticmethod
    def _get_smart_device_info(device):
        """Get S.M.A.R.T info for a specific device"""
        device_info = {
            'device': device,
            'health': 'UNKNOWN',
            'temperature': None,
            'power_on_hours': None,
            'raw_read_error_rate': None,
            'reallocated_sector_count': None,
        }
        
        try:
            result = subprocess.run(['smartctl', '-a', device], 
                                  capture_output=True, text=True, timeout=5)
            
            # Check health status
            if 'PASSED' in result.stdout:
                device_info['health'] = 'PASSED'
            elif 'FAILED' in result.stdout:
                device_info['health'] = 'FAILED'
            
            # Extract temperature
            temp_match = re.search(r'Temperature.*?:\s*(\d+)\s*Celsius', result.stdout)
            if temp_match:
                device_info['temperature'] = int(temp_match.group(1))
            
            # Extract power-on hours
            hours_match = re.search(r'Power_On_Hours.*?\s(\d+)\s', result.stdout)
            if hours_match:
                device_info['power_on_hours'] = int(hours_match.group(1))
            
            # Extract read error rate
            error_match = re.search(r'Raw_Read_Error_Rate.*?\s(\d+)\s', result.stdout)
            if error_match:
                device_info['raw_read_error_rate'] = int(error_match.group(1))
            
            # Extract reallocated sectors
            sector_match = re.search(r'Reallocated_Sector_Ct.*?\s(\d+)\s', result.stdout)
            if sector_match:
                device_info['reallocated_sector_count'] = int(sector_match.group(1))
                
        except Exception:
            pass
        
        return device_info
    
    @staticmethod
    def get_system_info():
        """Get basic system information"""
        return {
            'hostname': os.uname()[1],
            'system': os.uname()[0],
            'release': os.uname()[2],
            'machine': os.uname()[4],
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            'uptime_seconds': int(time.time() - psutil.boot_time()),
            'network': SystemMonitor._get_network_info(),
        }
    
    @staticmethod
    def _get_network_info():
        """Get network information (IP, DNS, Gateway)"""
        network_info = {
            'ip_address': 'N/A',
            'gateway': 'N/A',
            'dns': 'N/A',
        }
        
        try:
            # Get all network interfaces
            interfaces = psutil.net_if_addrs()
            # Look for eth0 or wlan0 (common on Raspberry Pi)
            for iface_name in ['eth0', 'wlan0', 'enp0s3', 'enp0s31f6']:
                if iface_name in interfaces:
                    for addr in interfaces[iface_name]:
                        if addr.family == 2:  # IPv4
                            network_info['ip_address'] = addr.address
                            break
                    break
            
            # If not found in common interfaces, get first available
            if network_info['ip_address'] == 'N/A':
                for iface_name, addrs in interfaces.items():
                    for addr in addrs:
                        if addr.family == 2:  # IPv4
                            if not addr.address.startswith('127.'):
                                network_info['ip_address'] = addr.address
                                break
                    if network_info['ip_address'] != 'N/A':
                        break
        except Exception as e:
            pass
        
        try:
            # Get gateway using netstat/ss or by reading routing table directly
            try:
                # Try reading from /proc/net/route directly
                with open('/proc/net/route', 'r') as f:
                    lines = f.readlines()
                    for line in lines[1:]:  # Skip header
                        fields = line.split()
                        # Destination 0.0.0.0 = default route
                        if fields[1] == '00000000':  # Default route
                            # Gateway is at index 2, in hex format
                            gw_hex = fields[2]
                            # Convert hex to IP
                            gw_int = int(gw_hex, 16)
                            gw_ip = '.'.join(str((gw_int >> (i*8)) & 0xff) for i in range(4))
                            if gw_ip != '0.0.0.0':
                                network_info['gateway'] = gw_ip
                                break
            except:
                pass
        except Exception as e:
            pass
        
        try:
            # Get DNS - try multiple methods
            dns_servers = []
            
            # Method 1: Try /etc/resolv.conf
            try:
                with open('/etc/resolv.conf', 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('nameserver '):
                            dns = line.replace('nameserver ', '').strip()
                            if dns and not dns.startswith('#'):
                                dns_servers.append(dns)
            except:
                pass
            
            # Method 2: Try systemd-resolve if available
            if not dns_servers:
                try:
                    result = subprocess.run(['resolvectl', 'status'], 
                                          capture_output=True, text=True, timeout=2)
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if 'DNS Servers:' in line:
                                parts = line.split()
                                for part in parts:
                                    if '.' in part and not part.startswith('DNS'):
                                        dns_servers.append(part)
                                        break
                except:
                    pass
            
            if dns_servers:
                network_info['dns'] = dns_servers[0]
        except Exception as e:
            pass
        
        return network_info
    
    @staticmethod
    def get_all_metrics():
        """Get all system metrics in one call"""
        return {
            'system_info': SystemMonitor.get_system_info(),
            'cpu': SystemMonitor.get_cpu_metrics(),
            'memory': SystemMonitor.get_memory_metrics(),
            'storage': SystemMonitor.get_storage_metrics(),
            'smart': SystemMonitor.get_smart_data(),
            'timestamp': datetime.now().isoformat()
        }
