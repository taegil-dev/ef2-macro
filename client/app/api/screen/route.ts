import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export async function GET(req: NextRequest) {
  const authHeader = req.headers.get('authorization') || '';

  const jwt = authHeader.startsWith('Bearer ') ? authHeader.slice(7) : '';
  if (!jwt) 
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

  const url = process.env.NEXT_PUBLIC_SUPABASE_URL!;
  const admin = createClient(
    url, 
    process.env.SUPABASE_SERVICE_ROLE_KEY!,
    { 
      auth: { 
        persistSession: false, 
        autoRefreshToken: false 
      } 
    } 
  );

  const { data: auth, error: authError } = await admin.auth.getUser(jwt);
  if (authError || !auth.user) 
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

  const deviceId = req.nextUrl.searchParams.get('deviceId') || '';
  if (!/^[a-zA-Z0-9_-]{1,80}$/.test(deviceId)) {
    return NextResponse.json({ error: 'Invalid device' }, { status: 400 });
  }

  // IMPORTANT: Adapt 'device_id' and 'owner_user_id' to your actual macro_devices schema.
  const { data: device, error: deviceError } = await admin.from('macro_devices')
    .select('device_id')
    .eq('device_id', deviceId)
    .eq('owner_user_id', auth.user.id)
    .maybeSingle();

  if (deviceError) {
    console.error('Device lookup failed:', {
      code: deviceError.code,
      message: deviceError.message,
      details: deviceError.details,
      hint: deviceError.hint,
    });

    return NextResponse.json(
      { error: 'Device lookup failed' },
      { status: 500 }
    );
  }

  if (!device) 
    return NextResponse.json({ error: 'Forbidden' }, { status: 403 });

  const { data, error } = await admin.storage.from('game-screens')
    .createSignedUrl(`${deviceId}/latest.jpg`, 10);

  if (error || !data) 
    return NextResponse.json({ error: 'No screenshot yet' }, { status: 404 });
  
  return NextResponse.json({ url: data.signedUrl, fetchedAt: new Date().toISOString() },
    { headers: { 'Cache-Control': 'no-store' } });
}
