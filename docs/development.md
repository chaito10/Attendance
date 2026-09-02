# Development

Everything about building, running, and releasing the project for developers.

## Project layout

```text
Attendance/
├── src/attendance/__init__.py   # The entire application (Flask + Waitress)
├── packaging/entry.py           # PyInstaller entry point
├── attendance.spec              # PyInstaller spec (committed for reproducibility)
├── docs/                        # This documentation site (MkDocs)
├── mkdocs.yml                   # MkDocs configuration
├── .github/workflows/
│   ├── docs.yml                 # Builds the docs site and deploys to GitHub Pages
│   └── release.yml              # Builds all platform binaries and uploads to a release
├── pyproject.toml               # Project metadata + dependencies (uv-managed)
└── uv.lock                      # Lockfile
```

## Running from source

Requires [uv](https://docs.astral.sh/uv/) on PATH.

```bash
uv sync                 # install runtime + dev dependencies
uv run attendance       # production server (Waitress)
uv run attendance --dev # Flask dev server
```

The app is a console command with these options:

```text
usage: attendance [-h] [--host HOST] [--port PORT] [--dev] [--threads THREADS]
```

## Testing

There is currently **no automated test suite** - the app is verified with a
manual smoke test. After starting the server:

- `curl -I http://127.0.0.1:5000/` should return `302` (redirect to `/login`).
- `curl http://127.0.0.1:5000/login` should return `200` with the login form.
- Login, start a session, scan, verify the CSV export.

## Building binaries locally

PyInstaller does **not cross-compile**: a Windows host can only build a Windows
binary. The released binaries are produced by CI (see below), but you can build
the binary for your current OS with:

```bash
uv run pyinstaller --onefile --console --name attendance --clean packaging/entry.py
```

The result appears in `dist/` (`attendance.exe` on Windows, `attendance` on
macOS/Linux).

## Cross-platform CI builds

`.github/workflows/release.yml` builds on **every tag push** (`v*`) and uploads
the binaries to the corresponding GitHub release:

| Runner | Artifact |
|--------|----------|
| `ubuntu-22.04` | `attendance-<version>-linux-x86_64.tar.gz` |
| `macos-14` (arm64) | `attendance-<version>-macos-arm64.tar.gz` |
| `macos-13` (x86_64) | `attendance-<version>-macos-x86_64.tar.gz` |
| `windows-latest` | `attendance-<version>-win64.zip` |

It also prints each artifact's **SHA-256** to the build log - used to update the
bucket manifest.

## Building the docs site

```bash
uv run mkdocs serve     # live preview at http://127.0.0.1:8000/
uv run mkdocs build     # static site into site/
```

The `site/` directory is gitignored; CI builds and deploys it to GitHub Pages
on every push to `main` (`.github/workflows/docs.yml`).

## Releasing a new version

1. Bump `version` in `pyproject.toml`.
2. Add a `CHANGELOG.md` entry.
3. Commit and push to `main`.
4. Create and push an annotated tag: `git tag -a v0.1.1 -m "v0.1.1"` then
   `git push origin v0.1.1`.
5. CI builds all platform binaries, creates the release, and attaches the
   artifacts.
6. Update the Scoop manifest in `chaito10/scoop-bucket` with the new version and
   the Windows zip hash from the build log.

## Contributing

- Run `uv sync` after checking out to get a working environment.
- Keep the app in `src/attendance/__init__.py` (it's intentionally single-file).
- Keep docs in sync with behavior changes - the site is user-facing.
- Run `uv run mkdocs build` before pushing docs changes.