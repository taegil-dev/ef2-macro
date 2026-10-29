import { NextRequest, NextResponse } from 'next/server';
import { admin, deviceAuth, error, noStore } from '../../../../../lib/server';

export async function GET(req: NextRequest) {
  if (!deviceAuth(req)) 
    return error('Unauthorized', 401);

  const { data, error: dbError } = await admin()
    .rpc('claim_macro_command', { p_device_id: process.env.DEVICE_ID! });

  if (dbError) 
    return error('Database error', 500);

  return NextResponse.json({ command: data?.[0] ?? null }, { headers: noStore });
}
