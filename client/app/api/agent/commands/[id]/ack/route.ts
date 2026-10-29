import { NextRequest, NextResponse } from 'next/server';
import { admin, deviceAuth, error, noStore } from '../../../../../../lib/server';

export async function POST(req: NextRequest, context: { params: Promise<{ id: string }> }) {
  if (!deviceAuth(req)) 
    return error('Unauthorized', 401);

  const { id } = await context.params;
  if (!/^[0-9a-f-]{36}$/i.test(id)) 
    return error('Invalid id');

  let body: any; 
  try { 
    body = await req.json(); 
  } catch { 
    return error('Invalid JSON'); 
  }

  if (!['done','failed'].includes(body.status)) 
    return error('Invalid status');

  const { data, error: dbError } = await admin()
    .from('macro_commands')
    .update({ 
      status: body.status, 
      error: String(body.error ?? '').slice(0,500), 
      completed_at: new Date().toISOString() 
    }).eq('id', id)
    .eq('device_id', process.env.DEVICE_ID!)
    .eq('status', 'claimed')
    .select('id');

  if (dbError) 
    return error('Database error', 500);

  return NextResponse.json({ ok: true, updated: (data?.length ?? 0) > 0 }, { headers: noStore });
}
