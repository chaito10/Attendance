#!/usr/bin/env python3
"""
Single-file QR Attendance System
--------------------------------
Install:
    pip install flask qrcode[pil] waitress

Run (production, via Waitress):
    attendance
    python -m attendance

Run (development, Flask dev server):
    attendance --dev
    python -m attendance --dev

Teacher dashboard:
    http://127.0.0.1:5000/
    Password protected (set ATTENDANCE_PASSWORD env var; a random
    password is printed at startup if not set).

Students:
    Scan the QR displayed on the teacher dashboard.
    Phones must be on the same Wi-Fi/LAN as the teacher PC.

Notes:
- Served with Waitress in production (multi-threaded, production-grade WSGI)
- SQLite database is created automatically as attendance.db
- CSV export is available from the teacher dashboard
- QR session token changes when a new session starts and expires when stopped
- A student can only be marked once per attendance session
- One registration per device (IP address) per session
- The teacher dashboard is locked behind a password; student scan
  links never expose the dashboard
- ATTENDANCE_PASSWORD: teacher dashboard password
- ATTENDANCE_SECRET: Flask session signing key (optional)
- ATTENDANCE_DB: path to the SQLite database file (optional)
"""

import argparse
import csv
import hashlib
import io
import os
import secrets
import socket
import sqlite3
import threading
import time
from datetime import datetime

import qrcode
from flask import (
    Flask,
    Response,
    redirect,
    render_template_string,
    request,
    session,
    url_for,
)
from waitress import serve

app = Flask(__name__)
app.secret_key = os.environ.get(
    "ATTENDANCE_SECRET", os.urandom(32).hex()
)
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

DB_FILE = os.environ.get("ATTENDANCE_DB") or os.path.join(
    os.getcwd(), "attendance.db"
)

# Password required to open the teacher dashboard. Override via
# ATTENDANCE_PASSWORD. A random password is generated and printed at
# startup if one is not configured.
TEACHER_PASSWORD = os.environ.get(
    "ATTENDANCE_PASSWORD"
) or os.environ.get("TEACHER_PASSWORD") or os.urandom(9).hex()

SESSION_DURATION_SECONDS = 10 * 60

state_lock = threading.Lock()
attendance_state = {
    "active": False,
    "token": None,
    "started_at": None,
    "expires_at": None,
}


def db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_token TEXT NOT NULL,
            student_id TEXT NOT NULL,
            student_name TEXT NOT NULL,
            marked_at TEXT NOT NULL,
            ip_address TEXT,
            UNIQUE(session_token, student_id),
            UNIQUE(session_token, ip_address)
        )
        """
    )
    # Migrate older databases that only enforce uniqueness per student ID.
    cols = [r[1] for r in conn.execute("PRAGMA table_info(attendance)").fetchall()]
    if "ip_address" in cols:
        indexes = {i[1] for i in conn.execute("PRAGMA index_list(attendance)").fetchall()}
        if "sqlite_autoindex_attendance_2" not in indexes:
            # Recreate the table to add the per-device (IP) unique constraint.
            conn.execute("ALTER TABLE attendance RENAME TO attendance_old")
            conn.execute(
                """
                CREATE TABLE attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_token TEXT NOT NULL,
                    student_id TEXT NOT NULL,
                    student_name TEXT NOT NULL,
                    marked_at TEXT NOT NULL,
                    ip_address TEXT,
                    UNIQUE(session_token, student_id),
                    UNIQUE(session_token, ip_address)
                )
                """
            )
            conn.execute(
                """
                INSERT INTO attendance
                    (id, session_token, student_id, student_name, marked_at, ip_address)
                SELECT id, session_token, student_id, student_name, marked_at, ip_address
                FROM attendance_old
                """
            )
            conn.execute("DROP TABLE attendance_old")
    conn.commit()
    conn.close()


def local_ip():
    """Best-effort LAN IP used in the QR URL."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def attendance_url():
    ip = local_ip()
    port = request.host.split(":")[-1] if ":" in request.host else "5000"
    token = state["token"]
    return f"http://{ip}:{port}/attend/{token}"


def client_ip():
    """Real client IP, honoring a single X-Forwarded-For proxy hop."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr


def teacher_authed():
    return session.get("teacher") is True


def require_teacher():
    """Redirect to the teacher login if the session is not authorized."""
    if not teacher_authed():
        return redirect(url_for("login"))
    return None


def current_state():
    with state_lock:
        return dict(attendance_state)


# Keep a short alias so templates/routes remain simple.
state = attendance_state


BASE_STYLE = """
<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    font-family: Arial, Helvetica, sans-serif;
    background: #f5f7fb;
    color: #172033;
}
.container {
    max-width: 1050px;
    margin: 30px auto;
    padding: 0 18px;
}
.card {
    background: white;
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 18px;
    box-shadow: 0 5px 20px rgba(0,0,0,.07);
}
h1, h2 { margin-top: 0; }
button, .button {
    border: 0;
    border-radius: 10px;
    padding: 12px 18px;
    font-size: 15px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    background: #172033;
    color: white;
}
button.danger, .danger { background: #b42318; }
button.success, .success { background: #147a4b; }
button.secondary, .secondary { background: #667085; }
input {
    width: 100%;
    padding: 13px;
    border: 1px solid #d0d5dd;
    border-radius: 9px;
    margin: 7px 0 15px;
    font-size: 16px;
}
label { font-weight: 600; }
.status {
    padding: 10px 14px;
    border-radius: 10px;
    display: inline-block;
    font-weight: bold;
}
.active { background: #d1fadf; color: #05603a; }
.inactive { background: #fee4e2; color: #912018; }
table {
    width: 100%;
    border-collapse: collapse;
}
th, td {
    padding: 11px;
    border-bottom: 1px solid #eaecf0;
    text-align: left;
}
.qr {
    display: block;
    width: min(420px, 90vw);
    height: auto;
    margin: 15px auto;
}
.center { text-align: center; }
.big { font-size: 22px; font-weight: 700; }
.muted { color: #667085; }
.message {
    padding: 14px;
    border-radius: 10px;
    background: #eef4ff;
    margin-bottom: 15px;
}
.actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}
@media (max-width: 700px) {
    .container { margin-top: 15px; }
    th, td { font-size: 13px; padding: 8px; }
}
</style>
"""


LOGIN = """
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Teacher Login</title>
    {{ style|safe }}
</head>
<body>
<div class="container">
    <div class="card">
        <h1>Teacher Login</h1>
        <p class="muted">Enter the teacher password to open the dashboard.</p>
        {% if message %}
            <div class="message">{{ message }}</div>
        {% endif %}
        <form method="post">
            <label for="password">Password</label>
            <input id="password" name="password" type="password" required autofocus
                   placeholder="Teacher password">
            <button class="success" type="submit">Unlock Dashboard</button>
        </form>
    </div>
</div>
</body>
</html>
"""


DASHBOARD = """
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="5">
    <title>QR Attendance</title>
    {{ style|safe }}
</head>
<body>
<div class="container">
    <div class="card">
        <h1>QR Attendance</h1>
        {% if active %}
            <span class="status active">● Attendance ACTIVE</span>
            <p class="muted">Started: {{ started }}</p>
            <p class="big">Students scanned: {{ count }}</p>

            <div class="center">
                <img class="qr" src="{{ url_for('qr_image') }}" alt="Attendance QR">
                <p class="muted">Students scan this QR code with their phone.</p>
                <p><strong>{{ attend_url }}</strong></p>
            </div>

            <form method="post" action="{{ url_for('stop') }}">
                <button class="danger" type="submit">Stop Attendance</button>
            </form>
        {% else %}
            <span class="status inactive">● Attendance NOT ACTIVE</span>
            <p class="muted">Start a session to generate a new QR code.</p>
            <form method="post" action="{{ url_for('start') }}">
                <button class="success" type="submit">Start Attendance</button>
            </form>
        {% endif %}
    </div>

    <div class="card">
        <h2>Today's Attendance</h2>
        <div class="actions">
            <a class="button secondary" href="{{ url_for('export_csv') }}">Export CSV</a>
        </div>
        <br>
        {% if rows %}
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Student ID</th>
                    <th>Name</th>
                    <th>Time</th>
                </tr>
            </thead>
            <tbody>
            {% for row in rows %}
                <tr>
                    <td>{{ loop.index }}</td>
                    <td>{{ row['student_id'] }}</td>
                    <td>{{ row['student_name'] }}</td>
                    <td>{{ row['marked_at'] }}</td>
                </tr>
            {% endfor %}
            </tbody>
        </table>
        {% else %}
            <p class="muted">No attendance recorded today.</p>
        {% endif %}
    </div>
</div>
</body>
</html>
"""


ATTEND = """
<!doctype html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Mark Attendance</title>
    {{ style|safe }}
</head>
<body>
<div class="container">
    <div class="card">
        <h1>Mark Attendance</h1>
        {% if message %}
            <div class="message">{{ message }}</div>
        {% endif %}

        {% if not active %}
            <p>Attendance is not currently active.</p>
        {% elif registered %}
            <div class="message">Attendance already recorded for this session on this device.</div>
        {% else %}
            <p class="muted">Enter the student details below.</p>
            <form method="post">
                <label for="student_id">Student ID / Roll Number</label>
                <input id="student_id" name="student_id" required autofocus
                       placeholder="e.g. 24CS001">

                <label for="student_name">Student Name</label>
                <input id="student_name" name="student_name" required
                       placeholder="Full name">

                <button class="success" type="submit">Mark Attendance</button>
            </form>
        {% endif %}
    </div>
</div>
</body>
</html>
"""


@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    if request.method == "POST":
        password = request.form.get("password", "")
        authorized = os.environ.get("ATTENDANCE_PASSWORD", os.environ.get("TEACHER_PASSWORD"))
        # Constant-time comparison against the configured/default password.
        given = hashlib.sha256(password.encode()).hexdigest()
        expected = hashlib.sha256(
            (authorized if authorized else TEACHER_PASSWORD).encode()
        ).hexdigest()
        if given == expected:
            session["teacher"] = True
            return redirect(url_for("dashboard"))
        message = "Incorrect password. Please try again."

    return render_template_string(
        LOGIN,
        style=BASE_STYLE,
        message=message,
    )


@app.post("/logout")
def logout():
    session.pop("teacher", None)
    return redirect(url_for("login"))


@app.route("/")
def dashboard():
    gate = require_teacher()
    if gate:
        return gate

    today = datetime.now().strftime("%Y-%m-%d")
    conn = db()
    rows = conn.execute(
        """
        SELECT student_id, student_name, marked_at
        FROM attendance
        WHERE marked_at LIKE ?
        ORDER BY id DESC
        """,
        (today + "%",),
    ).fetchall()
    conn.close()

    s = current_state()
    return render_template_string(
        DASHBOARD,
        style=BASE_STYLE,
        active=s["active"],
        started=(
            datetime.fromtimestamp(s["started_at"]).strftime("%H:%M:%S")
            if s["started_at"]
            else ""
        ),
        count=session_count(s["token"]) if s["token"] else 0,
        rows=rows,
        attend_url=(
            f"http://{local_ip()}:{request.host.split(':')[-1]}/attend/{s['token']}"
            if s["token"]
            else ""
        ),
    )


@app.post("/start")
def start():
    gate = require_teacher()
    if gate:
        return gate

    with state_lock:
        attendance_state["active"] = True
        attendance_state["token"] = secrets.token_urlsafe(12)
        attendance_state["started_at"] = time.time()
        attendance_state["expires_at"] = time.time() + SESSION_DURATION_SECONDS

    return redirect(url_for("dashboard"))


@app.post("/stop")
def stop():
    gate = require_teacher()
    if gate:
        return gate

    with state_lock:
        attendance_state["active"] = False
        attendance_state["token"] = None
        attendance_state["started_at"] = None
        attendance_state["expires_at"] = None

    return redirect(url_for("dashboard"))


@app.route("/qr.png")
def qr_image():
    gate = require_teacher()
    if gate:
        return gate

    s = current_state()
    if not s["active"] or not s["token"]:
        return Response(status=404)

    target = f"http://{local_ip()}:{request.host.split(':')[-1]}/attend/{s['token']}"

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(target)
    qr.make(fit=True)

    image = qr.make_image()
    output = io.BytesIO()
    image.save(output, format="PNG")
    output.seek(0)

    return Response(output.getvalue(), mimetype="image/png")


@app.route("/attend/<token>", methods=["GET", "POST"])
def attend(token):
    s = current_state()

    if (
        not s["active"]
        or not s["token"]
        or token != s["token"]
        or (s["expires_at"] and time.time() > s["expires_at"])
    ):
        return render_template_string(
            ATTEND,
            style=BASE_STYLE,
            active=False,
            message="This attendance QR code has expired or is no longer active.",
        )

    ip = client_ip()

    if request.method == "POST":
        already = already_registered(token, ip)
        if already:
            return render_template_string(
                ATTEND,
                style=BASE_STYLE,
                active=True,
                registered=True,
                message="This device has already marked attendance for this session.",
            )

        student_id = request.form.get("student_id", "").strip()
        student_name = request.form.get("student_name", "").strip()

        if not student_id or not student_name:
            return render_template_string(
                ATTEND,
                style=BASE_STYLE,
                active=True,
                message="Please enter both Student ID and Student Name.",
            )

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = db()
        try:
            conn.execute(
                """
                INSERT INTO attendance
                (session_token, student_id, student_name, marked_at, ip_address)
                VALUES (?, ?, ?, ?, ?)
                """,
                (token, student_id, student_name, now, ip),
            )
            conn.commit()
            message = "Attendance recorded successfully."
        except sqlite3.IntegrityError:
            if already_registered(token, ip):
                message = "This device has already marked attendance for this session."
            else:
                message = f"Attendance already recorded for Student ID {student_id}."
        finally:
            conn.close()

        return render_template_string(
            ATTEND,
            style=BASE_STYLE,
            active=True,
            registered=True,
            message=message,
        )

    registered = already_registered(token, ip)
    return render_template_string(
        ATTEND,
        style=BASE_STYLE,
        active=True,
        registered=registered,
        message=(
            "You have already marked attendance for this session on this device."
            if registered
            else ""
        ),
    )


def already_registered(token, ip):
    if not token or not ip:
        return False
    conn = db()
    row = conn.execute(
        "SELECT 1 FROM attendance WHERE session_token = ? AND ip_address = ? LIMIT 1",
        (token, ip),
    ).fetchone()
    conn.close()
    return row is not None


def session_count(token):
    if not token:
        return 0

    conn = db()
    row = conn.execute(
        "SELECT COUNT(*) AS c FROM attendance WHERE session_token = ?",
        (token,),
    ).fetchone()
    conn.close()
    return row["c"]


@app.route("/export.csv")
def export_csv():
    gate = require_teacher()
    if gate:
        return gate

    today = datetime.now().strftime("%Y-%m-%d")

    conn = db()
    rows = conn.execute(
        """
        SELECT student_id, student_name, marked_at, session_token, ip_address
        FROM attendance
        WHERE marked_at LIKE ?
        ORDER BY marked_at
        """,
        (today + "%",),
    ).fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        ["Student ID", "Student Name", "Marked At", "Session Token", "IP Address"]
    )

    for row in rows:
        writer.writerow(
            [
                row["student_id"],
                row["student_name"],
                row["marked_at"],
                row["session_token"],
                row["ip_address"],
            ]
        )

    filename = f"attendance_{today}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def session_expiry_worker():
    while True:
        time.sleep(1)
        with state_lock:
            if (
                attendance_state["active"]
                and attendance_state["expires_at"]
                and time.time() >= attendance_state["expires_at"]
            ):
                attendance_state["active"] = False
                attendance_state["token"] = None
                attendance_state["started_at"] = None
                attendance_state["expires_at"] = None


def main(argv=None):
    parser = argparse.ArgumentParser(description="QR Attendance System")
    parser.add_argument(
        "--host", default="0.0.0.0", help="host/interface to bind (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=5000, help="port to bind (default: 5000)"
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="run the Flask development server instead of Waitress",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=4,
        help="Waitress thread count (default: 4)",
    )
    args = parser.parse_args(argv)

    init_db()

    threading.Thread(
        target=session_expiry_worker,
        daemon=True,
    ).start()

    print()
    print("=" * 60)
    print("QR ATTENDANCE SYSTEM")
    print("=" * 60)
    print(f"Teacher dashboard: http://127.0.0.1:{args.port}/")
    print(f"LAN dashboard:     http://{local_ip()}:{args.port}/")
    print()
    print("The teacher dashboard is password protected.")
    if not os.environ.get("ATTENDANCE_PASSWORD") and not os.environ.get(
        "TEACHER_PASSWORD"
    ):
        print(f"Teacher password (auto-generated): {TEACHER_PASSWORD}")
        print("Set ATTENDANCE_PASSWORD to use your own.")
    else:
        print("Use your configured ATTENDANCE_PASSWORD to log in.")
    print()
    print("Students must be connected to the same Wi-Fi/LAN.")
    print("Press Ctrl+C to stop.")
    print("=" * 60)
    print()

    if args.dev:
        app.run(host=args.host, port=args.port, debug=False, threaded=True)
    else:
        serve(app, host=args.host, port=args.port, threads=args.threads)


if __name__ == "__main__":
    main()
