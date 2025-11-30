from flask import Blueprint, render_template, jsonify, request
from .system_monitor import SystemMonitor
import subprocess
import os

bp = Blueprint('main', __name__)

# Password for shutdown (set to default, can be overridden)
SHUTDOWN_PASSWORD = os.environ.get('SHUTDOWN_PASSWORD', 'raspberry')

@bp.route('/')
def index():
    """Render main dashboard page"""
    return render_template('dashboard.html')

@bp.route('/api/metrics/all')
def get_all_metrics():
    """Get all system metrics"""
    return jsonify(SystemMonitor.get_all_metrics())

@bp.route('/api/metrics/cpu')
def get_cpu_metrics():
    """Get CPU metrics"""
    return jsonify(SystemMonitor.get_cpu_metrics())

@bp.route('/api/metrics/memory')
def get_memory_metrics():
    """Get memory metrics"""
    return jsonify(SystemMonitor.get_memory_metrics())

@bp.route('/api/metrics/storage')
def get_storage_metrics():
    """Get storage metrics"""
    return jsonify(SystemMonitor.get_storage_metrics())

@bp.route('/api/metrics/system')
def get_system_info():
    """Get system information"""
    return jsonify(SystemMonitor.get_system_info())

@bp.route('/api/system/reboot', methods=['POST'])
def reboot_system():
    """Reboot the system"""
    try:
        subprocess.Popen(['sudo', 'reboot'])
        return jsonify({'status': 'success', 'message': 'System rebooting...'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/api/system/shutdown', methods=['POST'])
def shutdown_system():
    """Shutdown the system with password verification"""
    try:
        data = request.get_json()
        password = data.get('password', '')
        
        if password != SHUTDOWN_PASSWORD:
            return jsonify({'status': 'error', 'message': 'Invalid password'}), 401
        
        subprocess.Popen(['sudo', 'shutdown', '-h', 'now'])
        return jsonify({'status': 'success', 'message': 'System shutting down...'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
