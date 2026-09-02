# Using the app

## Starting the server

Run the `attendance` command (or `attendance.exe` on Windows) in a terminal:

```text
attendance
```

The console prints a banner with the dashboard addresses and the teacher
password:

```text
============================================================
QR ATTENDANCE SYSTEM
============================================================
Teacher dashboard: http://127.0.0.1:5000/
LAN dashboard:     http://192.168.1.42:5000/
...
Teacher password (auto-generated): 4f8a2c9d1b6e
...
```

Press **Ctrl+C** to stop.

### Command-line options

| Flag | Default | Description |
|------|---------|-------------|
| `--host` | `0.0.0.0` | Interface to bind. Use `127.0.0.1` to keep it local-only. |
| `--port` | `5000` | Port to bind. |
| `--threads` | `4` | Waitress worker threads (production only). |
| `--dev` | off | Use the Flask development server instead of Waitress. |

## Teacher dashboard

1. Open `http://127.0.0.1:5000/` in a browser.
2. Enter the **teacher password** shown at startup (or your configured
   `ATTENDANCE_PASSWORD`).
3. The dashboard shows:
   - The current session status (**active** / **not active**)
   - The live QR code and the scan URL
   - The number of students scanned so far
   - **Today's attendance** table with an **Export CSV** button

## Running an attendance session

1. Click **Start Attendance** - a new QR code is generated with a fresh,
   single-use session token.
2. Students connect their phones to the **same Wi-Fi/LAN** as the server.
3. Each student scans the QR and enters:
   - **Student ID / Roll Number** (e.g. `24CS001`)
   - **Student Name**
4. Click **Stop Attendance** when done. The QR (and its token) becomes invalid
   immediately.

!!! tip "Session expiry"
    A session automatically ends after **10 minutes**, even if you forget to stop
    it. The QR on the dashboard then reports that it has expired.

### Scan behavior

The app enforces two anti-abuse rules:

- **One registration per device** - each IP address can mark attendance at most
  once per session.
- **One registration per student** - each Student ID can be recorded at most
  once per session.

Students who have already marked attendance (or who try a second time) see a
message instead of the form.

## Exporting to CSV

Click **Export CSV** on the dashboard to download `attendance_YYYY-MM-DD.csv`
with that day's records:

```text
Student ID,Student Name,Marked At,Session Token,IP Address
24CS001,Aarav Pawar,2026-09-02 10:31:05,<token>,192.168.1.15
```

## Storing data

Attendance is stored in a **single SQLite file**, `attendance.db`, created in
the directory you launched the server from. The database is created and
migrated automatically at startup.

Use `ATTENDANCE_DB` to point at a different location (useful under
[systemd](install/linux.md#run-as-a-systemd-service-optional) or Docker).

## Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `ATTENDANCE_PASSWORD` | random at startup | Teacher dashboard password. Use for a fixed password. |
| `TEACHER_PASSWORD` | same as `ATTENDANCE_PASSWORD` | Legacy alias for the teacher password. |
| `ATTENDANCE_SECRET` | random at startup | Flask session signing key. Set it to keep logins valid across restarts. |
| `ATTENDANCE_DB` | `attendance.db` in the working directory | Path to the SQLite database file. |

!!! warning "Security model"
    This tool is designed for a **trusted classroom LAN**. The session token in
    the QR URL is the only thing that authorizes a student submission, and the
    teacher interface is protected by the dashboard password - but there is no
    per-student login. Do not expose port 5000 to the public internet.

## Networking

- The QR code points to the server's **LAN IP** (auto-detected) so phones can
  reach it.
- Students must be on the **same network** as the server; they cannot scan from
  outside the LAN.
- The server binds `0.0.0.0` (all interfaces) by default. See each platform's
  install guide for firewall instructions:
  - [Windows](install/windows.md#firewall)
  - [Linux](install/linux.md#firewall)
  - [macOS](install/macos.md#firewall)

[Next: API Reference](api.md)