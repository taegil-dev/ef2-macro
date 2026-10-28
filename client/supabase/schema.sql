-- Run once in Supabase SQL Editor. Replace YOUR_AUTH_USER_UUID below after signing up.
create table if not exists public.macro_devices (
  id text primary key,
  owner_id uuid not null references auth.users(id),
  status text not null default 'idle' check (status in ('idle','running')),
  last_seen_at timestamptz,
  last_error text not null default ''
);
create table if not exists public.macro_commands (
  id uuid primary key default gen_random_uuid(),
  device_id text not null references public.macro_devices(id),
  owner_id uuid not null references auth.users(id),
  type text not null check (type in ('CLICK','START_REPEAT','STOP','SWIPE')),
  payload jsonb not null default '{}'::jsonb,
  status text not null default 'pending' check (status in ('pending','claimed','done','failed','expired')),
  priority integer not null default 0,
  error text not null default '',
  created_at timestamptz not null default now(),
  claimed_at timestamptz,
  completed_at timestamptz,
  expires_at timestamptz not null default (now() + interval '60 seconds')
);
create index if not exists macro_command_queue_idx on public.macro_commands(device_id,status,priority desc,created_at);
alter table public.macro_devices enable row level security;
alter table public.macro_commands enable row level security;
-- No browser-facing table policies: access is via authenticated Next.js API routes.
create or replace function public.claim_macro_command(p_device_id text)
returns table (id uuid, type text, payload jsonb)
language plpgsql security definer set search_path = public
as $$
begin
  update public.macro_commands set status = 'expired'
  where device_id = p_device_id and status = 'pending' and expires_at < now();
  return query
  with candidate as (
    select c.id from public.macro_commands c
    where c.device_id = p_device_id and c.status = 'pending' and c.expires_at >= now()
    order by c.priority desc, c.created_at asc
    limit 1 for update skip locked
  ), updated as (
    update public.macro_commands c set status = 'claimed', claimed_at = now()
    from candidate where c.id = candidate.id
    returning c.id, c.type, c.payload
  ) select u.id, u.type, u.payload from updated u;
end;
$$;
revoke all on function public.claim_macro_command(text) from public, anon, authenticated;
grant execute on function public.claim_macro_command(text) to service_role;
-- After creating your Supabase Auth account, run separately with YOUR actual UUID:
-- insert into public.macro_devices (id, owner_id) values ('my-windows-pc', 'YOUR_AUTH_USER_UUID');
