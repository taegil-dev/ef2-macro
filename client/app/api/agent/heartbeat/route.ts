import { NextRequest, NextResponse } from 'next/server';
import { admin, deviceAuth, error, noStore } from '../../../../lib/server';

type Device = {
  id: string;
  owner_id: string;
  status: string;
  last_seen_at: string;
  last_error: string;
  screen_viewed_at: string | null;
};

export async function POST(req: NextRequest) {
  if (!deviceAuth(req))
    return error('Unauthorized', 401);

  let body: any;

  try {
    body = await req.json();
  } catch {
    return error('Invalid JSON');
  }

  if (!['idle', 'running'].includes(body.status))
    return error('Invalid status');

  const { data: device, error: dbError } = await admin()
    .from('macro_devices')
    .update({
      status: body.status,
      last_error: String(body.last_error ?? '').slice(0, 500),
      last_seen_at: new Date().toISOString()
    })
    .eq('id', process.env.DEVICE_ID!)
    .select('id, status, last_seen_at, last_error, screen_viewed_at')
    .single<Device>();

  if (dbError || !device)
    return error('Database error', 500);

  const watching =
    !!device.screen_viewed_at &&
    Date.now() - new Date(device.screen_viewed_at).getTime() < 25000;

  return NextResponse.json(
    {
      ok: true,
      screen_watching: watching
    },
    { headers: noStore }
  );
}