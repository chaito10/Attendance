# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.3.0] - 2026-09-07

### Added

- **Subjects** — teachers can add/delete subjects (e.g. Mathematics, Physics)
  and assign each attendance session to a subject
- **Multiple sessions per subject per day** — start and stop a session, then
  start another session for the same subject the same day
- **Per-subject monthly report** — the monthly report now sums each student's
  attendance per subject (total sessions), with a student × subject matrix and
  per-subject drill-down showing session dates and distinct days
- Subject-aware CSV exports (`/monthly.csv` in matrix or per-subject form), and
  the daily export (`/export.csv`) now includes a `Subject` column

### Changed

- Monthly report view: switched from "distinct days across all sessions" to a
  per-subject breakdown; legacy attendance rows are backfilled to a `General`
  subject during migration
- Version bumped to 0.3.0

## [v0.2.0] - 2026-09-07

### Added

- Monthly attendance report on the teacher dashboard with a month picker,
  showing per-student distinct days attended
- CSV export of the monthly compilation (`/monthly.csv`)

### Changed

- Version bumped to 0.2.0

## [v0.1.1] - 2026-09-02

### Added

- Documentation site (MkDocs + Material) with install guides for Windows, Linux,
  and macOS, a usage guide, HTTP API reference, and development notes
- Documentation site published to GitHub Pages
  (https://chaito10.github.io/Attendance/)
- Cross-platform release pipeline (GitHub Actions) that builds and attaches
  Windows, Linux x86_64, macOS arm64, and macOS x86_64 binaries to each release

### Changed

- Version bumped to 0.1.1

## [v0.1.0] - 2026-09-02

### Added

- Teacher dashboard to start/stop attendance sessions and generate a QR code
- Students scan the QR and submit their ID + name to mark attendance
- Password-protected teacher dashboard (env var configurable)
- One attendance registration per device (IP) per session
- SQLite persistence and CSV export of the day's attendance
- Production serving via Waitress (multi-threaded)
- Standalone Windows binary built with PyInstaller
- Scoop install manifest (`chaito10/scoop-bucket`)
