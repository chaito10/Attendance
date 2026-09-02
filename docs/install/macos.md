# Installing on macOS

Requirements: **macOS 12 Monterey or newer**. No Python is required for the
pre-built binary.

Choose the archive that matches your Mac:

| Mac | Architecture | Archive |
|-----|--------------|---------|
| Apple Silicon (M1/M2/M3/M4) | arm64 | `attendance-v0.1.1-macos-arm64.tar.gz` |
| Intel | x86_64 | `attendance-v0.1.1-macos-x86_64.tar.gz` |

## Install the binary

1. Download the archive for your architecture from the
   [releases page](https://github.com/chaito10/Attendance/releases/latest):

   ```bash
   curl -L -o attendance-v0.1.1-macos-arm64.tar.gz \
     https://github.com/chaito10/Attendance/releases/download/v0.1.1/attendance-v0.1.1-macos-arm64.tar.gz
   ```

2. Extract it and make it executable:

   ```bash
   tar xzf attendance-v0.1.1-macos-arm64.tar.gz
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

## Gatekeeper note

The binary is **not notarized**, so macOS may block the first launch with
"attendance cannot be opened because the developer cannot be verified". Fix it
once, either by:

- Hold **Control**, click the binary, and choose **Open**, then **Open** again, or
- Remove the quarantine attribute:

  ```bash
  xattr -d com.apple.quarantine ./attendance
  ```

## From source

Requires [uv](https://docs.astral.sh/uv/) and Git. `uv` will download its own
Python - your system Python version does not matter:

```bash
git clone https://github.com/chaito10/Attendance.git
cd Attendance
uv sync
uv run attendance
```

## Firewall

If macOS prompts, allow **incoming connections** for `attendance` so phones on
the same LAN can reach the server on **port 5000** (System Settings -> Network
-> Firewall).

[Next: Using the app](../usage.md)