# QR Attendance System

A **single-file, local Wi-Fi QR attendance system** for classrooms. The teacher
starts an attendance session from a password-protected dashboard, students scan
a QR code with their phones, and the class list is recorded in a local SQLite
database and exportable to CSV.

No cloud, no accounts, no student data leaving the classroom network.

## Key features

- **Runs entirely on one computer** - a teacher laptop or classroom PC
- **QR-based check-in** - students scan the on-screen QR and enter their ID/name
- **Password-protected dashboard** - student scan links never expose the controls
- **One registration per device** per session (an IP can't mark twice)
- **One registration per student** per session (duplicate IDs are rejected)
- **Sessions expire automatically** after 10 minutes
- **CSV export** of the day's attendance
- **Served by Waitress** in production (multi-threaded, production-grade WSGI)
- **Cross-platform** - Windows, Linux, and macOS binaries

## Platform support

| Platform | Binary | Install |
|----------|--------|---------|
| Windows | `attendance-v0.1.1-win64.zip` | [Scoop](install/windows.md) or [manual](install/windows.md) |
| Linux x86_64 | `attendance-v0.1.1-linux-x86_64.tar.gz` | [Manual](install/linux.md) |
| macOS arm64 | `attendance-v0.1.1-macos-arm64.tar.gz` | [Manual](install/macos.md) |
| macOS x86_64 | `attendance-v0.1.1-macos-x86_64.tar.gz` | [Manual](install/macos.md) |
| Any (from source) | Python with uv | [Development](development.md) |

> **Newest release:** [v0.1.1](https://github.com/chaito10/Attendance/releases/latest)
> - all binaries are attached to the release page.

## Quick start

1. **Install** the app for your platform (see [Installation](index.md#installation)).
2. **Run** it from your terminal.
3. The console shows a **teacher password** (auto-generated on first run unless you
   set `ATTENDANCE_PASSWORD`).
4. Open `http://127.0.0.1:5000/` and log in with that password.
5. Click **Start Attendance**, then **Stop** when students are done.
6. Connect a phone to the **same Wi-Fi/LAN**, scan the QR, and enter student details.

Hold down **Ctrl+C** to stop the server.

## Installation

See the per-platform guides:

- [Windows](install/windows.md)
- [Linux](install/linux.md)
- [macOS](install/macos.md)

## Learn more

- [Usage guide](usage.md) - starting sessions, scanning, environment variables
- [API Reference](api.md) - every HTTP endpoint the app exposes
- [Development](development.md) - run from source and build binaries