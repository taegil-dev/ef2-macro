import { createClient } from '@supabase/supabase-js';
import { createHash, timingSafeEqual } from 'node:crypto';
import { NextRequest, NextResponse } from 'next/server';

export const admin = () => createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!,
    { 
      auth: { autoRefreshToken: false, persistSession: false } }
);

export function error(message: string, status = 400) {
    return NextResponse.json({ error: message }, { status, headers: { 'Cache-Control': 'no-store' } });
}

export function deviceAuth(req: NextRequest) {
    const token = req.headers.get('authorization')?.replace(/^Bearer\s+/i, '') ?? '';
    const expected = process.env.DEVICE_TOKEN ?? '';

    const id = req.headers.get('x-device-id') ?? '';

    if (!expected || expected.length < 24 || !token || id !== process.env.DEVICE_ID) 
      return false;

    const a = createHash('sha256').update(token).digest();
    const b = createHash('sha256').update(expected).digest();
    return timingSafeEqual(a, b);
}

export async function userAuth(req: NextRequest) {
    const token = req.headers.get('authorization')?.match(/^Bearer\s+(.+)$/i)?.[1];
    if (!token) 
      return null;

    const { data, error } = await admin().auth.getUser(token);
    if (error || !data.user) 
      return null;

    // The first setup is intentionally single-owner: set owner UID in the DB row.
    const { data: device } = await admin()
      .from('macro_devices')
      .select('id')
      .eq('id', process.env.DEVICE_ID!)
      .eq('owner_id', data.user.id)
      .maybeSingle();
      
    return device ? data.user : null;
}

export const noStore = { 'Cache-Control': 'no-store' };
