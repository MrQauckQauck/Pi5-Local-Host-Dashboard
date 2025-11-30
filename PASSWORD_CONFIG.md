# Shutdown Button Password Configuration

This guide explains how to change the password required for the shutdown button on the Local Host Dashboard.

## Default Password

The default password is: `raspberry`

## Methods to Change the Password

### Method 1: Environment Variable (Recommended - Temporary)

Set the password via environment variable before running the dashboard:

```bash
# In your terminal
export SHUTDOWN_PASSWORD="your_new_password"

# Then run the dashboard
python run.py
```

**Advantages:**
- No file modifications required
- Easy to test different passwords
- Password not stored in version control

**Disadvantages:**
- Password resets when terminal closes or Pi reboots
- Must be set manually each time

---

### Method 2: Systemd Service Configuration (Recommended - Permanent)

Edit the systemd service file to set the password permanently:

```bash
# Edit the systemd service
sudo nano /etc/systemd/system/dashboard.service
```

Find the `[Service]` section and add the `Environment` line:

```ini
[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Local-Host-Dashboard
ExecStart=/home/pi/Local-Host-Dashboard/venv/bin/python run.py
Restart=always
RestartSec=10
Environment="SHUTDOWN_PASSWORD=your_new_password"
```

**Apply the changes:**

```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Restart the dashboard service
sudo systemctl restart dashboard

# Verify it's running
sudo systemctl status dashboard
```

**Advantages:**
- Password persists through reboots
- Automatically applied when service starts
- Only need to configure once

**Disadvantages:**
- Requires sudo access to edit service file
- Password visible in system file (consider file permissions)

---

### Method 3: Using a .env File

Create a `.env` file in the dashboard directory:

```bash
# Navigate to dashboard directory
cd /home/pi/Local-Host-Dashboard

# Create .env file
nano .env
```

Add this line to `.env`:

```
SHUTDOWN_PASSWORD=your_new_password
```

**Install python-dotenv (if not already installed):**

```bash
source venv/bin/activate
pip install python-dotenv
```

**Update run.py to load .env file:**

Edit `run.py` and add at the top:

```python
from dotenv import load_dotenv
import os

load_dotenv()
```

**Advantages:**
- Password in local file (not in version control if .env is in .gitignore)
- Can manage multiple environment variables
- Easy to share configuration template

**Disadvantages:**
- Requires additional package (python-dotenv)
- File must be present for password to work

---

## Checking Current Password in Code

The password is validated in `app/routes.py`:

```python
@bp.route('/api/system/shutdown', methods=['POST'])
def shutdown_system():
    password = request.json.get('password', '')
    expected_password = os.environ.get('SHUTDOWN_PASSWORD', 'raspberry')
    
    if password != expected_password:
        return {'error': 'Invalid password'}, 401
    
    # Perform shutdown
    subprocess.run(['sudo', 'shutdown', '-h', 'now'], check=True)
    return {'message': 'Shutdown initiated'}
```

## Security Best Practices

1. **Strong Passwords**: Use a password that's not easily guessable
   - ✅ Good: `MyD@shb0ard#2025`
   - ❌ Bad: `password123` or `raspberry`

2. **Access Control**: 
   - Only share the password with trusted users
   - Consider the dashboard URL should also be secured

3. **Service File Permissions**:
   - If using Method 2, ensure service file is only readable by root:
   ```bash
   sudo chmod 600 /etc/systemd/system/dashboard.service
   ```

4. **HTTPS (Future Enhancement)**:
   - Consider adding SSL/TLS encryption for production use
   - This prevents password from being sent in plain text

## Troubleshooting

### Password not working after change

1. **Verify environment variable is set:**
   ```bash
   echo $SHUTDOWN_PASSWORD
   ```

2. **Check systemd service configuration:**
   ```bash
   sudo systemctl cat dashboard
   ```

3. **Restart the service:**
   ```bash
   sudo systemctl restart dashboard
   ```

4. **Check dashboard logs:**
   ```bash
   sudo journalctl -u dashboard -f
   ```

### Still using default password?

Make sure you've restarted the dashboard service after making changes:

```bash
sudo systemctl restart dashboard
```

## Quick Reference

| Method | Command | Persistence |
|--------|---------|------------|
| Environment Variable | `export SHUTDOWN_PASSWORD="pass"` | Session only |
| Systemd Service | Edit `/etc/systemd/system/dashboard.service` | Permanent ✅ |
| .env File | Create `Local-Host-Dashboard/.env` | Permanent ✅ |

## Example Workflow

### Change password using Systemd (Recommended):

```bash
# 1. Edit service file
sudo nano /etc/systemd/system/dashboard.service

# 2. Add/update Environment line with new password
# Environment="SHUTDOWN_PASSWORD=MyNewPass123"

# 3. Save (Ctrl+O, Enter, Ctrl+X)

# 4. Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart dashboard

# 5. Verify
sudo systemctl status dashboard

# 6. Test in browser - use new password in shutdown modal
```

Done! Your new password is now active.
