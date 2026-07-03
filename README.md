# entra-id-lifecycle-cli

> ⚠️ **Early-stage / work in progress.** Auth flow and user export are functional; provisioning, deprovisioning, and audit modules are still in development.

## What this is

A Python CLI for automating identity lifecycle management (Joiner–Mover–Leaver) in Microsoft Entra ID via the Microsoft Graph API, with audit reporting for stale accounts and excessive permissions.

Built as a hands-on companion to SC-300 study — the goal is to reflect how these workflows actually look in practice (least privilege, dry-run safety, idempotency), not a toy demo.

## Status

- [x] App registration + client credentials auth flow (MSAL)
- [x] Paginated user export → CSV
- [ ] Joiner / Mover / Leaver provisioning
- [ ] Stale account audit (`signInActivity`)
- [ ] Excessive permissions audit (role assignments)
- [ ] Access review report (HTML)
- [ ] Unit tests

## Stack

- Python
- `msal` — token acquisition (client credentials flow)
- `requests` — raw Graph API calls (no SDK, deliberately — keeps the API mechanics visible)
- Planned: `typer` (CLI), `jinja2` / `pandas` (reports)

## Setup

```bash
git clone <repo>
cd entra-id-lifecycle-cli
pip install -r requirements.txt
cp .env.example .env  # fill in TENANT_ID, CLIENT_ID, CLIENT_SECRET
```

Required Graph API permissions (**Application**, not Delegated):

- `User.ReadWrite.All`
- `Group.ReadWrite.All`
- `Directory.Read.All`
- `AuditLog.Read.All`
- `RoleManagement.Read.Directory`

## Why this exists

Bridging the gap between IAM theory and hands-on Entra ID / Graph API work — this repo tracks that process openly, including what isn't built yet.
