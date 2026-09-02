# QR Attendance

![Version](https://img.shields.io/github/v/release/chaito10/Attendance)
![License](https://img.shields.io/github/license/chaito10/Attendance)
![Docs](https://img.shields.io/badge/docs-gh--pages-1f6feb)
![Platforms](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-lightgrey)

A single-file QR-based attendance system for small classrooms. Teachers start an
attendance session on their PC, display a QR code, and students scan it with their
phones (on the same Wi-Fi/LAN) to mark themselves present.

Built with **Flask**, served in production by **Waitress**, with a **SQLite**
database.

> **Documentation:** [chaito10.github.io/Attendance](https://chaito10.github.io/Attendance)

## Features

- Teacher dashboard to start/stop attendance sessions and generate the QR code
- Students mark attendance by scanning the QR and entering their ID + name
- **Password-protected teacher dashboard** — student scan links never expose it
- **One registration per device** (IP address) per session — rescanning with a
  different ID cannot double-register
- Attendance is written to a local SQLite database
- CSV export of the day's attendance
- Sessions auto-expire after 10 minutes

## Install

Standalone binaries for **Windows, Linux x86_64, and macOS (arm64 & x86_64)** are
attached to every [release](https://github.com/chaito10/Attendance/releases/latest).
See the [install guides](https://chaito10.github.io/Attendance/install/windows/) for
full instructions.

### Windows (Scoop)

```bash
scoop bucket add chaito10 https://github.com/chaito10/scoop-bucket
scoop install attendance
```

### Windows / Linux / macOS (download)

Download `attendance-v0.1.1-win64.zip` (Windows), or the
`attendance-v0.1.1-linux-x86_64.tar.gz` / `attendance-v0.1.1-macos-arm64.tar.gz` /
`attendance-v0.1.1-macos-x86_64.tar.gz` archives for Unix, from the
[releases page](https://github.com/chaito10/Attendance/releases/latest). On Unix:

```bash
tar xzf attendance-v0.1.1-linux-x86_64.tar.gz
chmod +x attendance
./attendance
```

### From source

Requires Python 3.10+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Run

After installing via Scoop, run the packaged Windows binary:

```bash
attendance
```

From source (production, via Waitress, multi-threaded):

```bash
uv run attendance
```

Development (Flask dev server):

```bash
uv run attendance --dev
```

Optional flags:

| Flag        | Default | Description                                   |
|-------------|---------|-----------------------------------------------|
| `--host`    | `0.0.0.0` | Interface to bind                          |
| `--port`    | `5000`  | Port to bind                                  |
| `--threads` | `4`     | Waitress worker threads                       |
| `--dev`     | off     | Use the Flask dev server instead of Waitress  |

## How it works

1. The teacher opens the dashboard (`http://<pc-ip>:5000/`) and logs in with the
   teacher password.
2. Clicking **Start Attendance** generates a session token and a QR code whose URL
   points to `http://<pc-ip>:5000/attend/<token>`.
3. Students scan the QR with their phone and submit their ID and name. The entry is
   written to the database.
4. Clicking **Stop Attendance** invalidates the session. Sessions also auto-expire
   after 10 minutes.
5. The teacher can export the day's attendance as CSV from the dashboard.

The QR is encoded with the PC's LAN IP, so students' phones must be on the same
network. The teacher may also share the printed URL directly.

## Configuration (environment variables)

| Variable             | Description                                             |
|----------------------|---------------------------------------------------------|
| `ATTENDANCE_PASSWORD`| Teacher password for the dashboard. If unset, a random one is generated and printed at startup. |
| `ATTENDANCE_SECRET`  | Flask session signing key. Optional; generated at runtime if unset. |
| `ATTENDANCE_DB`      | Path to the SQLite database file. Defaults to `attendance.db` in the working directory. |

Example:

```bash
ATTENDANCE_PASSWORD="hunter2" ATTENDANCE_DB="/srv/attendance/attendance.db" uv run attendance
```

## Security notes

- The teacher dashboard (`/`, `/start`, `/stop`, `/export.csv`, `/qr.png`) requires
  a valid teacher login session. Unauthenticated visits are redirected to `/login`.
- The student route (`/attend/<token>`) requires no login, but is only usable while
  a session is active and the token matches.
- One attendance entry is allowed per device (IP address) per session, enforced by a
  database constraint in addition to application logic.
- Token secrecy: anyone with the session token can mark attendance while the session
  is active, which is the intended behavior for a classroom QR flow.

## Project structure

```
src/attendance/__init__.py   # the entire application (single file)
attendance.db                # SQLite database (created at runtime)
pyproject.toml               # build + dependency metadata
packaging/entry.py           # PyInstaller entry point
attendance.spec              # PyInstaller spec
docs/                        # documentation site (MkDocs)
mkdocs.yml                   # MkDocs configuration
.github/workflows/docs.yml   # builds & deploys the docs site to GitHub Pages
.github/workflows/release.yml# builds & attaches Windows/Linux/macOS binaries
```

## Build a binary

PyInstaller cannot cross-compile, so the released binaries are built in CI
(`.github/workflows/release.yml`) on each `v*` tag for Windows, Linux x86_64,
macOS arm64, and macOS x86_64. To build a binary for your current OS locally:

```bash
uv sync --group dev
uv run PyInstaller --onefile --console --name attendance --clean packaging/entry.py
```

## License

[MIT](LICENSE)

