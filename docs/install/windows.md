# Installing on Windows

Requirements: **Windows 10 or 11 (64-bit)**. No Python is required for the
pre-built binary.

## Option A - Scoop (recommended)

If you don't have [Scoop](https://scoop.sh) yet, install it first (in PowerShell):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex
```

Add the `chaito10` bucket and install:

```powershell
scoop bucket add chaito10 https://github.com/chaito10/scoop-bucket
scoop install attendance
```

Then launch it from any terminal:

```text
attendance
```

Scoop keeps the app up to date with `scoop update && scoop update attendance`.

## Option B - Manual (zip)

1. Download
   [`attendance-v0.1.1-win64.zip`](https://github.com/chaito10/Attendance/releases/download/v0.1.1/attendance-v0.1.1-win64.zip)
   from the [releases page](https://github.com/chaito10/Attendance/releases/latest).
2. Extract the archive (right-click -> **Extract All**).
3. Double-click `attendance.exe`, or run it from a terminal:

   ```powershell
   .\attendance.exe
   ```

4. The QR code and dashboard are served on `http://127.0.0.1:5000/`
   (or your LAN IP if students need to scan from their phones).

## Option C - From source

Requires [uv](https://docs.astral.sh/uv/) and Git:

```powershell
git clone https://github.com/chaito10/Attendance.git
cd Attendance
uv sync
uv run attendance
```

## Firewall

Students scan on their phones over the LAN, so Windows must allow inbound
connections to the server port (default **5000**) on Private networks. Windows
will usually prompt you when the server starts - check the **Private networks**
box. If you missed it:

1. Open **Windows Security** -> **Firewall & network protection**.
2. **Allow an app through the firewall** -> **Allow another app**.
3. Browse to `attendance.exe`, add it, and enable **Private**.

## Verifying the download

The official SHA-256 of `attendance-v0.1.1-win64.zip` is published with each
[release](https://github.com/chaito10/Attendance/releases/latest). Verify it
for yourself:

```powershell
Get-FileHash .\attendance-v0.1.1-win64.zip -Algorithm SHA256
```

[Next: Using the app](../usage.md)