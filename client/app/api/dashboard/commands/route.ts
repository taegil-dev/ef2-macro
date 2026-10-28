import { NextRequest, NextResponse } from 'next/server';
import { admin, userAuth, error, noStore } from '../../../../lib/server';
const ratio = (n: unknown) => typeof n === 'number' && Number.isFinite(n) && n >= 0 && n <= 1;
const range = (n: unknown, min: number, max: number) => typeof n === 'number' && Number.isFinite(n) && n >= min && n <= max;
export async function POST(req: NextRequest) {
  const user = await userAuth(req);
  if (!user) return error('Unauthorized', 401);
  let body: any; try { body = await req.json(); } catch { return error('Invalid JSON'); }
  const type = body.type, p = body.payload ?? {};
  if (!['CLICK','START_REPEAT','STOP','SWIPE'].includes(type)) return error('Unsupported command');
  if (type === 'CLICK' || type === 'START_REPEAT') {
    if (!ratio(p.x) || !ratio(p.y) || !range(p.duration, .01, .5)) return error('Invalid click parameters');
    if (type === 'START_REPEAT' && !range(p.interval, .1, 3600)) return error('Invalid interval');
  }
  if (type === 'SWIPE' && (!ratio(p.start_x) || !ratio(p.start_y) || !ratio(p.end_x) || !ratio(p.end_y) || !range(p.duration, .05, 5) || !Number.isInteger(p.steps) || p.steps < 2 || p.steps > 120)) return error('Invalid swipe parameters');
  // Avoid queuing stale repeated actions; STOP is placed ahead of pending commands.
  const db = admin();
  const { data, error: dbError } = await db.from('macro_commands').insert({ device_id: process.env.DEVICE_ID!, owner_id: user.id, type, payload: p, expires_at: new Date(Date.now() + 60000).toISOString(), priority: type === 'STOP' ? 10 : 0 }).select('id,status').single();
  if (dbError) return error('Database error', 500);
  return NextResponse.json({ command: data }, { status: 201, headers: noStore });
}
