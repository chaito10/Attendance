# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
