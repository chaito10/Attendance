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
   - A **Subjects** card to add/delete subjects
   - **Today's attendance** table (with the subject for each entry) and an
     **Export CSV** button
   - A **Monthly Report** link that opens the monthly compilation

## Subjects

Attendance sessions belong to a subject. Under the **Subjects** card on the
dashboard you can add subjects (e.g. Mathematics, Physics, Chemistry) and delete
them. Deleting a subject is only allowed while it has no attendance records.

When a session starts you can pick which subject it belongs to. You can run
**multiple sessions for the same subject on the same day** - just stop one
session and start another. If no subject is created yet, sessions are assigned
to the default **General** subject.

## Running an attendance session

1. (Optional) Add a subject and select it from the dropdown.
2. Click **Start Attendance** - a new QR code is generated with a fresh,
   single-use session token for that subject.
3. Students connect their phones to the **same Wi-Fi/LAN** as the server.
4. Each student scans the QR and enters:
   - **Student ID / Roll Number** (e.g. `24CS001`)
   - **Student Name**
5. Click **Stop Attendance** when done. The QR (and its token) becomes invalid
   immediately. Start another session (same or different subject) whenever
   needed in the same class period.

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
Student ID,Student Name,Subject,Marked At,Session Token,IP Address
24CS001,Aarav Pawar,Mathematics,2026-09-02 10:31:05,<token>,192.168.1.15
```

## Monthly report

Click **Monthly Report** on the dashboard. Use the month picker to select a
month (it defaults to the current month).

- With **All subjects** selected the report is a **student × subject matrix**:
  each cell is the number of sessions that student attended for that subject in
  the month, with a **Total** column.
- Select a **specific subject** to see a per-student breakdown for that subject
  only: total **sessions attended**, **distinct days** (multiple sessions the
  same day count as one day), and the session dates.

Click **Export CSV** on the monthly report to download the same data:

```text
Student ID,Student Name,Mathematics,Physics,Total
24CS001,Aarav Pawar,18,12,30
```

or, for a single subject:

```text
Student ID,Student Name,Sessions Attended,Distinct Days,Session Dates
24CS001,Aarav Pawar,2,1,2026-09-01 (2)
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