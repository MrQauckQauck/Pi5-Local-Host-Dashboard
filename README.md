# Update : create a new theme kind of pop os feel and added a favicon along with Network speed 

Still working on getting the Pi-hole intergration. 

# Local Host Dashboard - Raspberry Pi System Monitory 

web-based dashboard for monitoring Raspberry Pi 5 system metrics in real-time. Perfect for educational demonstrations and system administration.

Over the last few years, I’ve been tinkering with Raspberry Pis and using them for various purposes, and all of them are running headless. This can make it difficult to monitor them, so I decided it would be fun to create a local web page to provide a faster way to check and see what’s going on with my Pis.

<img width="1471" height="1016" alt="Screenshot 2025-12-08 at 16 24 23" src="https://github.com/user-attachments/assets/906fbb45-3bb7-439d-bb14-c084dd96408c" />

<img width="1452" height="875" alt="Screenshot 2025-12-08 at 15 30 46" src="https://github.com/user-attachments/assets/de4c9690-0085-452e-adbd-75ffeff36e43" />

<img width="1536" height="657" alt="Screenshot 2025-12-08 at 15 30 56" src="https://github.com/user-attachments/assets/ed53cf08-d33c-4a43-abfb-b4985ca49711" />


# Note: 

SMART data is not available for microSD cards because they lack the firmware and controller logic to track and report health metrics like hard drives or SSDs. To monitor SD card health, you need to rely on indirect methods such as checking for read/write errors, monitoring performance, or running file system checks. However, if you are using an SSD, SMART should work — but not tested

## Features

### CPU Monitoring
- Real-time temperature tracking with visual gauge
- Per-core CPU usage display
- Current, minimum, and maximum clock frequencies
- CPU voltage monitoring
- Throttling detection and alerts
  - Under-voltage detection
  - Frequency capping alerts
  - Thermal throttling status
  - Real-time throttling warnings

### Memory Monitoring
- RAM usage with detailed breakdown (used, available, cached)
- Swap usage tracking
- Excessive swap detection and alerts
- Memory pressure indicators

### Storage Monitoring
- Multi-partition disk space visualization
- Used/Free/Total storage display
- Filesystem type information
- Disk I/O performance metrics
  - Read/Write operation counts
  - Read/Write throughput (MB)
  - Read/Write time metrics

### Storage Health
- S.M.A.R.T data display (if available)
- Device health status
- Temperature monitoring per device
- Power-on hours tracking
- Bad sector detection
- Read error rate monitoring

### System Information
- Hostname and system details
- Uptime display
- Boot time information
- Release and machine information

## Requirements

- Raspberry Pi 5
- Python 3.7+
- Virtual environment (recommended)
- Network access (optional, for remote access)

## Installation

### 1. Clone or Download the Dashboard

```bash
cd /home/pi/Local-Host-Dashboard
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Optional: Install S.M.A.R.T Tools

For S.M.A.R.T data monitoring:

```bash
sudo apt-get update
sudo apt-get install smartmontools
```

### 5. Run the Dashboard

```bash
python run.py
```

The dashboard will start on `http://localhost:5002`

### Access from Another Machine

```bash
python run.py --host 0.0.0.0 --port 5000
```

Then access it from another computer on the network:
```
http://<raspberry-pi-ip>:5002
```

## Usage Examples

**Local access only:**
```bash
python run.py --host 127.0.0.1
```

**Network-accessible on custom port:**
```bash
python run.py --host 0.0.0.0 --port 8080
```

**Debug mode for development:**
```bash
python run.py --debug
```

## Dashboard Interface

The dashboard provides a clean, professional interface organized into sections:

### Header
- System hostname
- Current uptime
- Last update timestamp

### System Information Card
- Operating system details
- Machine architecture
- Boot time
- System release information

### CPU Metrics Card
- Temperature gauge (color-coded: green/yellow/red)
- Average CPU usage bar chart
- Per-core usage breakdown
- Current/Min/Max frequencies
- Voltage display
- Throttling status indicators

### Memory & Swap Card
- RAM usage with breakdown (used, available, cached)
- Swap usage tracking
- Excessive swap alerts
- Visual progress bars with color coding

### Storage Card
- Disk partition overview with usage percentages
- Free/Used/Total space per partition
- I/O performance statistics
- Read/Write operation counts and throughput

### Storage Health Card
- S.M.A.R.T device information
- Health status (PASSED/FAILED/UNKNOWN)
- Temperature per device
- Power-on hours and error metrics
- Bad sector tracking

## Auto-Start on Boot (Optional)

### Using systemd

Create `/etc/systemd/system/dashboard.service`:

```ini
[Unit]
Description=Local Host Dashboard
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Local-Host-Dashboard
Environment="PATH=/home/pi/Local-Host-Dashboard/venv/bin"
ExecStart=/home/pi/Local-Host-Dashboard/venv/bin/python run.py --host 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable dashboard
sudo systemctl start dashboard
sudo systemctl status dashboard
```

To view logs:
```bash
sudo journalctl -u dashboard -f
```

## Troubleshooting

### Dashboard shows "--" for some values
- Some metrics may require elevated privileges
- S.M.A.R.T data requires `smartctl` to be installed
- Temperature readings require `/sys/class/thermal` or `vcgencmd` access

### "Permission denied" errors
- Run with `sudo` for full access to throttling and thermal data
- Or add your user to appropriate groups:
  ```bash
  sudo usermod -a -G video $USER
  ```

### Module not found errors
- Make sure virtual environment is activated
- Reinstall requirements: `pip install -r requirements.txt`

### Dashboard not accessible from network
- Ensure firewall allows port 5000 (or your chosen port)
- Use `--host 0.0.0.0` when starting the server
- Check Raspberry Pi's IP: `hostname -I`

## Performance Considerations

- Update interval: 2 seconds (adjustable in `static/dashboard.js`)
- Lightweight API responses
- No database required
- Suitable for continuous monitoring
- Works well on Raspberry Pi 5

## Security Considerations

For production/classroom use:

1. **Network Access**: Restrict network access via firewall
2. **HTTPS**: Use a reverse proxy (nginx, Apache) with SSL/TLS
3. **Authentication**: Add authentication layer if needed
4. **Read-Only**: The dashboard only reads system metrics (no configuration changes)

Example nginx reverse proxy with SSL:
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert;
    ssl_certificate_key /path/to/key;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
## Project Structure

```
Local-Host-Dashboard/
├── app/
│   ├── __init__.py         # Flask app factory
│   ├── routes.py           # API endpoints
│   └── system_monitor.py   # System metrics collection
├── static/
│   ├── styles.css          # Dashboard styling
│   └── dashboard.js        # Frontend logic and updates
├── templates/
│   └── dashboard.html      # Main HTML template
├── run.py                  # Application entry point
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Development

To modify the dashboard:

1. **Frontend changes**: Edit `templates/dashboard.html`, `static/styles.css`, `static/dashboard.js`
2. **Backend changes**: Edit `app/system_monitor.py` or `app/routes.py`
3. **Add new metrics**: Extend `SystemMonitor` class in `app/system_monitor.py`

## License

Open source - feel free to modify and distribute.

## Support

For issues or questions:
1. Check this README
2. Review browser console for JavaScript errors (F12)
3. Check Flask logs for backend errors
4. Verify all dependencies are installed

## Changelog

### v1.0.0
- Initial release
- CPU, Memory, Storage monitoring
- S.M.A.R.T data support
- Throttling detection
- Professional responsive UI
- Real-time updates
- Educational interface design
