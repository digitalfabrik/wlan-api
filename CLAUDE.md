# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup & Running

```bash
python3 -m venv venv
source venv/bin/activate
pip install .

# Config must exist at Flask's instance_path (typically ./instance/config.yml)
# Copy config.yml to instance/config.yml and adjust credentials
mkdir -p instance && cp config.yml instance/config.yml

FLASK_APP=wlan_api.server flask run
```

**External dependency:** The PDF merging step requires `/usr/bin/pdfjam` (a LaTeX-based CLI tool) to be installed on the system.

## Architecture

The app is a Flask server with two blueprints:

- **`/vpg`** — Voucher PDF Generation. Takes a `roll` (batch number) and `count`, deterministically generates voucher codes, renders them as A5 PDF pages, merges them 2×2 onto A4 with an uploaded ads PDF using `pdfjam`, and returns the final PDF for download.
- **`/stats`** — Simple plaintext endpoint showing new user counts per month from the `radacct` table.

### Voucher lifecycle

1. **Generate** (`wlan_api/generate/__init__.py`): Codes are derived deterministically via HMAC-SHA256 keyed on `(roll, index)` — same roll+count always produces the same codes. The key and alphabet are in `config.yml`.
2. **PDF** (`wlan_api/pdf/VoucherPrint.py`): Renders each voucher as an A5 ReportLab document. The logo is loaded from `assets/images/TaT_DF_LOGO.jpeg`. `validity_days` comes from `config.yml` and is displayed in the voucher text.
3. **Activation** (`wlan_api/activation/__init__.py`): Inserts vouchers into a FreeRADIUS MySQL database (`radcheck` table). Validity is stored as `Max-All-Session` in seconds (`validity_days * 86400`). Aborts the entire batch if any voucher already exists.

### Config (`config.yml` / `instance/config.yml`)

Key fields under `VOUCHER`: `alphabet`, `length`, `key` (base64-encoded HMAC key), `validity_days`.

## Deployment

Das Deployment läuft über [Salt](https://saltproject.io). Die Salt-Konfiguration liegt in einem separaten Repository unter `/home/aniel_ehne/salt` (nicht in diesem Repo). Die relevanten Salt-States und Pillars für WLAN befinden sich dort unter:

- `states/wlan-captiveportal/` — Nginx-Konfiguration für das Captive Portal
- `states/wlan-freeradius/` — FreeRADIUS + MariaDB Installation
- `states/wlan-openvpn/` — OpenVPN-Konfiguration inkl. Client-Config-Dir pro Standort
- `pillars/admins/wlan.sls`, `pillars/backup/org/tuerantuer/wlan/`, `pillars/letsencrypt/org/tuerantuer/wlan/` — Pillar-Daten

### Standalone PDF generation script

`scripts/generate.py` reads voucher codes from a CSV (semicolon-delimited, `#` for comments) and writes a PDF — bypasses the web UI and database entirely.
