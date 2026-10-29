# Game Macro PC Agent (Windows)

A Windows Python agent that **polls an authenticated HTTPS API** for commands and sends background mouse messages to the `CROSVM_1` child window of Google Play Games. No inbound PC port, port forwarding, or Tailscale is needed.

## Install

1. Install Python 3.11+ on Windows.
2. In PowerShell, from this folder:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   Copy-Item .env.example .env
   ```
3. Edit `.env`: set `API_BASE_URL`, `DEVICE_ID`, `DEVICE_TOKEN`. Keep `DRY_RUN=true` initially.
4. Run: `python agent.py`.
5. After backend commands work, set `DRY_RUN=false` and run again. Leave the game open (not minimized).

**IMPORTANT:** This is the PC agent only. You must deploy an API implementing the protocol below before it can receive remote commands. Vercel static hosting alone does not provide a command queue. Never put the device token in browser-side code. Don't commit `.env` to Git.

## Backend API contract

All requests contain `Authorization: Bearer <DEVICE_TOKEN>` and `X-Device-ID: <DEVICE_ID>`. The server must validate both, authorize the device, and implement atomic command claiming to prevent duplicate execution. The PC polls approximately once per second.

- `POST {API_BASE_URL}/heartbeat` JSON: `{"status":"idle|running", "last_error":""}`. Return 2xx.
- `GET {API_BASE_URL}/commands/next` returns `{"command":null}` or `{"command":{"id":"unique-id", "type":"CLICK", "payload":{"x":0.5,"y":0.5}}}`.
- `POST {API_BASE_URL}/commands/{id}/ack` JSON: `{"status":"done"}` or `{"status":"failed","error":"..."}`. Return 2xx.

Supported command types:

```json
{"type":"CLICK", "payload":{"x":0.5,"y":0.5,"duration":0.05}}
{"type":"START_REPEAT", "payload":{"x":0.5,"y":0.5,"interval":1.0,"duration":0.05}}
{"type":"STOP", "payload":{}}
{"type":"SWIPE", "payload":{"start_x":0.2,"start_y":0.5,"end_x":0.8,"end_y":0.5,"duration":0.5,"steps":30}}
```

Coordinates are normalized from 0 to 1 relative to the `CROSVM_1` client area. `START_REPEAT` continues until STOP or process termination. `done` for START_REPEAT means **accepted and started**, not that the loop completed. Only one repeating task runs at a time. STOP takes effect when polled, not instantaneously.

## Limitations

- Windows only for real clicks; `DRY_RUN=true` can be used elsewhere for API integration tests.
- Google Play Games must be running and not minimized; the `CROSVM_1` class must exist.
- Click was observed working by the user; swipe remains unverified.
- `PostMessage` does not prove the game acted; the API acknowledges message submission only.
- This is a minimal agent, not a hardened job system. For production, the server should add command expiration, replay protection, per-device ACL, atomic leases/ack semantics, rate limiting, and audit logging. A lost acknowledgement may require backend deduplication.
