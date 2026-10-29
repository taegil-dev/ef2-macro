import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import { timingSafeEqual } from 'node:crypto';

export const runtime = 'nodejs';
const bucket = 'game-screens';
function equal(a: string, b: string) {
  const x = Buffer.from(a), y = Buffer.from(b);
  return x.length === y.length && timingSafeEqual(x, y);
}
export async function POST(req: NextRequest) {
  // Single-device reference authentication. Replace with your existing heartbeat
  // device verifier for multi-device deployments.
  const deviceId = req.headers.get('x-device-id') || '';
  const token = req.headers.get('x-device-token') || '';
  if (!process.env.AGENT_DEVICE_ID || !process.env.AGENT_DEVICE_TOKEN ||
      !equal(deviceId, process.env.AGENT_DEVICE_ID) ||
      !equal(token, process.env.AGENT_DEVICE_TOKEN)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  if (req.headers.get('content-type') !== 'image/jpeg') {
    return NextResponse.json({ error: 'JPEG required' }, { status: 415 });
  }
  const bytes = Buffer.from(await req.arrayBuffer());
  if (!bytes.length || bytes.length > 2_000_000 || bytes[0] !== 0xff || bytes[1] !== 0xd8) {
    return NextResponse.json({ error: 'Invalid or oversized JPEG' }, { status: 400 });
  }
  const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.SUPABASE_SERVICE_ROLE_KEY!,
    { auth: { persistSession: false, autoRefreshToken: false } });
  const path = `${deviceId}/latest.jpg`;
  const { error } = await supabase.storage.from(bucket).upload(path, bytes, {
    contentType: 'image/jpeg', upsert: true, cacheControl: '0',
  });
  if (error) return NextResponse.json({ error: 'Storage upload failed' }, { status: 500 });
  return NextResponse.json({ ok: true });
}
