import { NextRequest, NextResponse } from 'next/server';
import { admin, userAuth, error, noStore } from '../../../../lib/server';

export async function GET(req: NextRequest) {
  if (!await userAuth(req)) 
    return error('Unauthorized', 401);

  const db = admin();
  const [device, commands] = await Promise.all([
    db.from('macro_devices')
      .select('id,status,last_seen_at,last_error')
      .eq('id', process.env.DEVICE_ID!)
      .single(),
    db.from('macro_commands')
      .select('id,type,payload,status,error,created_at,completed_at')
      .eq('device_id', process.env.DEVICE_ID!)
      .order('created_at', { ascending: false })
      .limit(10)
  ]);

  if (device.error || commands.error) 
    return error('Database error', 500);

  return NextResponse.json({ device: device.data, commands: commands.data }, { headers: noStore });
}
