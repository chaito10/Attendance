# Installing on Linux

Requirements: a **64-bit x86_64** Linux distribution with glibc (Ubuntu,
Debian, Fedora, Arch, etc.). No Python is required for the pre-built binary.

## Install the binary

1. Download the archive from the
   [releases page](https://github.com/chaito10/Attendance/releases/latest):

   ```bash
   curl -L -o attendance-v0.1.1-linux-x86_64.tar.gz \
     https://github.com/chaito10/Attendance/releases/download/v0.1.1/attendance-v0.1.1-linux-x86_64.tar.gz
   ```

2. Extract it and make it executable:

   ```bash
   tar xzf attendance-v0.1.1-linux-x86_64.tar.gz
   chmod +x attendance
   ```

3. Run it:

   ```bash
   ./attendance
   ```

4. Open the dashboard at `http://127.0.0.1:5000/`, or use your LAN IP if
   students need to scan from their phones.

### Install to PATH (optional)

```bash
sudo install -m 0755 attendance /usr/local/bin/attendance
```

Then just type `attendance` from anywhere.

## Run as a systemd service (optional)

Create `/etc/systemd/system/attendance.service`:

```ini
[Unit]
Description=QR Attendance System
After=network.target

[Service]
Type=simple
Environment=ATTENDANCE_DB=/var/lib/attendance/attendance.db
ExecStart=/usr/local/bin/attendance --host 0.0.0.0 --port 5000
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Then enable and start it:

```bash
sudo systemctl enable --now attendance
sudo systemctl status attendance
```

## From source

Requires [uv](https://docs.astral.sh/uv/) and Git:

```bash
git clone https://github.com/chaito10/Attendance.git
cd Attendance
uv sync
uv run attendance
```

## Firewall

Open port **5000** so phones on the same LAN can reach the server:

- **ufw (Ubuntu/Debian):** `sudo ufw allow 5000/tcp`
- **firewalld (Fedora/RHEL):** `sudo firewall-cmd --permanent --add-port=5000/tcp && sudo firewall-cmd --reload`

## Verifying the download

```bash
sha256sum attendance-v0.1.1-linux-x86_64.tar.gz
```

Compare the output against the hash published on the
[release page](https://github.com/chaito10/Attendance/releases/latest).

[Next: Using the app](../usage.md)