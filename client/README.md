# MacroDeck — Vercel + Supabase remote control

This Next.js project implements the exact HTTP protocol expected by the **previously delivered Python PC Agent**. No port forwarding or Tailscale required. The browser sends commands to authenticated Next.js API routes; the PC Agent polls those routes. All data is stored in Supabase PostgreSQL.

## 1. Supabase

1. Create a Supabase project.
2. Under Authentication > Users, create your **own** email/password user. Copy its UUID.
3. In SQL Editor, execute `supabase/schema.sql`.
4. Then execute (replace UUID):
   ```sql
   insert into public.macro_devices (id, owner_id)
   values ('my-windows-pc', 'YOUR_AUTH_USER_UUID');
   ```
5. In Project Settings > API, copy the Project URL, publishable/anon key and **secret service_role key**. Keep the service_role key private.

## 2. Vercel

1. Push this folder to a private GitHub repository or import it via Vercel CLI.
2. Framework: Next.js. Build: `npm run build`.
3. Add these environment variables from `.env.example` to Vercel:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY` (server-only)
   - `DEVICE_ID` (same as PC Agent)
   - `DEVICE_TOKEN` (long random secret, server-only)
4. Redeploy after setting environment variables.

Generate the device token with `py -c "import secrets; print(secrets.token_urlsafe(48))"` and put the **same value** in both Vercel and the PC Agent's `.env`.

## 3. PC Agent

Update the previous agent's `.env`:
```dotenv
API_BASE_URL=https://YOUR-DEPLOYMENT.vercel.app/api/agent
DEVICE_ID=my-windows-pc
DEVICE_TOKEN=THE_SAME_LONG_RANDOM_TOKEN
GAME_TITLE=오늘도 환생 2
TARGET_CLASS=CROSVM_1
POLL_SECONDS=1
HEARTBEAT_SECONDS=15
DRY_RUN=true
```
Start `python agent.py`. Confirm the dashboard shows **online** and test commands with `DRY_RUN=true`; then set `DRY_RUN=false` and restart the agent to enable actual game input. The game must remain open, not minimized.

## 4. Test

1. Log into the deployed website with the Supabase user you created.
2. Dashboard should show PC online within 15–20 seconds after the agent starts.
3. Send a single click. In the agent console, look for `[DRY RUN] click ...`.
4. Send START_REPEAT, then STOP; check recent commands.
5. Disable dry-run to control the actual game window.

## Security and operational notes

- Browser Supabase login uses access tokens, which are validated on the server via `auth.getUser`.
- Only the `owner_id` of the configured device can use dashboard endpoints.
- The Python agent authenticates with a separate bearer device token; it is **never sent to the browser**.
- Supabase tables have RLS enabled and no browser-facing policies. Server routes use service_role.
- SQL RPC atomically claims commands (`FOR UPDATE SKIP LOCKED`) to avoid concurrent delivery.
- Commands expire after 60 seconds if not claimed; `STOP` has priority over pending commands.
- `done` for START_REPEAT means accepted/started, not that it has stopped. State is reported via heartbeat.
- This MVP is for one device and one owner; device IDs and secrets are configured as environment variables.
- Do not expose your service_role or device token in frontend variables or commit `.env`.
- Vercel Functions are stateless; the queue and online state live in Supabase.
- PC Agent's 1-second polling can cause substantial Vercel invocation counts. For sustained 24/7 usage, increase `POLL_SECONDS` to 3–5 or implement realtime push.
- The current agent can lose an in-flight command if it crashes after claim and before ack; it will remain `claimed`. This design deliberately avoids automatically replaying input commands to prevent accidental duplicate clicks.
- This application has no screen capture or image matching yet.
