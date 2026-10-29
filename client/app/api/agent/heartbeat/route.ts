import { NextRequest, NextResponse } from 'next/server';
import { admin, deviceAuth, error, noStore } from '../../../../lib/server';

export async function POST(req: NextRequest) {
  if (!deviceAuth(req)) 
    return error('Unauthorized', 401);

  let body: any;
  try { 
    body = await req.json(); 
  } catch { 
    return error('Invalid JSON'); 
  }

  if (!['idle','running'].includes(body.status)) 
    return error('Invalid status');
  
  const { error: dbError } = await admin()
    .from('macro_devices')
    .update({ 
      status: body.status, 
      last_error: String(body.last_error ?? '').slice(0,500), 
      last_seen_at: new Date().toISOString() 
    }).eq('id', process.env.DEVICE_ID!);

  if (dbError) 
    return error('Database error', 500);
  
  return NextResponse.json({ ok: true }, { headers: noStore });
}
