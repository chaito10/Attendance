# API Reference

The app exposes a small HTTP interface. Everything is **form/HTML based** - there
is **no JSON API**. Teacher-only endpoints return a `302` redirect to `/login`
when a valid teacher session isn't present.

Base URL: `http://<server>:5000/` (port configurable with `--port`).

## Endpoints

### `GET /login`

Teacher login page. Returns the login form (HTML).

### `POST /login`

Verifies the teacher password.

| Field | Type | Description |
|-------|------|-------------|
| `password` | string | The teacher password (`ATTENDANCE_PASSWORD`). |

Responses:

- Correct password -> `302` redirect to `/` and sets the teacher session cookie.
- Wrong password -> `200` with the login form and an *Incorrect password* message.

### `POST /logout`

Clears the teacher session and `302` redirects to `/login`.

### `GET /` (dashboard)

Requires a teacher session. Renders the dashboard: session status, QR code,
scanned count, and today's attendance table.

Responses:

- No teacher session -> `302` to `/login`.
- Teacher session -> `200` HTML dashboard.

### `POST /start`

Requires a teacher session. Starts a new attendance session with a fresh token
and a 10-minute expiry, then `302` redirects to `/`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `subject_id` | int | no | The subject this session belongs to. Defaults to `General`. |

### `POST /stop`

Requires a teacher session. Ends the current session and invalidates its token,
then `302` redirects to `/`.

### `POST /subjects/add`

Requires a teacher session. Adds a subject, then `302` redirects to `/`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Subject name (must be unique). |

### `POST /subjects/<subject_id>/delete`

Requires a teacher session. Deletes a subject, then `302` redirects to `/`.
Rejected while the subject still has attendance records.

### `GET /qr.png`

Requires a teacher session. Serves the current session's QR code.

Responses:

- Session active -> `200` `image/png`.
- No active session -> `404`.

The QR encodes the current attend URL:
`http://<lan-ip>:<port>/attend/<token>`.

### `GET /attend/<token>`

Public (student-facing). Validates the token and renders the check-in page.

Responses:

- Invalid, expired, or stopped session -> `200` HTML stating the QR has expired.
- Valid session, device not yet used -> `200` HTML form with `student_id` and
  `student_name` fields.
- Valid session, device already used -> `200` HTML *already recorded* message
  (no form).

### `POST /attend/<token>`

Public (student-facing). Records an attendance entry.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `student_id` | string | yes | Student ID / roll number. |
| `student_name` | string | yes | Full name. |

Behavior:

- Token must match the active session and not be expired.
- **One entry per IP address** per session (the client IP, honoring one
  `X-Forwarded-For` hop).
- **One entry per `student_id`** per session.

Responses: always `200` HTML with a status message (success, duplicate device,
duplicate student, or missing fields).

### `GET /export.csv`

Requires a teacher session. Downloads the day's attendance as a CSV attachment:

`attendance_YYYY-MM-DD.csv`

```text
Student ID,Student Name,Subject,Marked At,Session Token,IP Address
```

### `GET /monthly`

Requires a teacher session. Renders the monthly attendance report.

Query params:

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `month` | string | current month | The month to report, `YYYY-MM`. |
| `subject` | int | none | A subject ID. When omitted, renders the student × subject matrix (each cell = sessions attended that month). When set, renders the per-student breakdown for that subject: sessions attended, distinct days, and session dates. |

### `GET /monthly.csv`

Requires a teacher session. Downloads the monthly compilation as a CSV
attachment, matching the current report view:

`attendance_YYYY-MM.csv` (matrix, when no subject is selected)

```text
Student ID,Student Name,Mathematics,Physics,Total
```

`attendance_<subject>_YYYY-MM.csv` (single subject)

```text
Student ID,Student Name,Sessions Attended,Distinct Days,Session Dates
```

## Authentication

- **Teacher endpoints:** gated by a signed session cookie flag (`teacher=true`),
  set after a successful `/login`. The password comparison uses SHA-256 with
  constant-time behavior.
- **Student endpoints:** gated only by the single-use **session token** embedded
  in the QR URL. There is no per-student login.

## Client IP detection

`client_ip()` returns `X-Forwarded-For` (first hop only, trimmed) when present,
otherwise the socket remote address. This lets the app run behind a single
reverse proxy while still enforcing one entry per device.

## Session lifecycle

- Sessions last **10 minutes** and are auto-expired by a background worker even
  if `POST /stop` is never called.
- A stopped or expired session invalidates its token immediately - old QR codes
  stop working.

## Error handling

There are no JSON error codes. Every failure path renders an HTML page with a
plain-language message. Do not screen-scrape the responses; use the forms as the
app's intended interface.