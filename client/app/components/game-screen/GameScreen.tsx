'use client';
import { useEffect, useState } from 'react';

export default function GameScreen({ supabase, deviceId, online }: { supabase: any; deviceId: string; online: boolean }) {
  const [src, setSrc] = useState<string | null>(null);
  const [status, setStatus] = useState('연결 중...');
  const [delay, setDelay] = useState(60000);
  const [delayChanged, setDelayChanged] = useState(false);
  const [changeDelay, setChangeDelay] = useState(false);

  const [screenStart, setScreenStart] = useState(false);

  function handleDelayChange(e: React.ChangeEvent<HTMLInputElement>) {
    setDelay(Number(e.target.value));
    setDelayChanged(true);

    if (!changeDelay) {
      setChangeDelay(true);
      setTimeout(() => {
        setChangeDelay(false);
        setDelayChanged(false);
        setScreenStart(prev => !prev); // Trigger screen refresh
      }, 1000);
    }
  }

  useEffect(() => {
    let active = true;
    const poll = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession();
        if (!session) 
          throw new Error('로그인이 필요합니다');
        
        const res = await fetch(`/api/screen?deviceId=${encodeURIComponent(deviceId)}`, {
          headers: { Authorization: `Bearer ${session.access_token}` }, cache: 'no-store',
        });
        if (!res.ok) 
          throw new Error(`화면 조회 실패 (${res.status})`);

        const data = await res.json();
        if (active) { 
          setSrc(data.url); 
          setStatus(`마지막 조회: ${new Date().toLocaleTimeString()}`); 
        }
      } catch (e) {
        if (active) 
          setStatus(e instanceof Error ? e.message : '화면 조회 오류');
      }
    };

    if (online) {
      void poll();
    } else {
      setStatus('장치가 오프라인입니다');
      return;
    }

    const timer = window.setInterval(() => {
      if (online) {
        void poll();
      }
    }, delay);

    return () => { active = false; window.clearInterval(timer); };
  }, [screenStart, deviceId, online]);

  return (
    <section className="game-screen">
      <div className={`delay-info ${delayChanged ? 'delay-info-changed' : ''}`}>
        <p style={{ margin: 0 }}>딜레이: {delay / 1000}초</p>
      </div>
      <input className="delay-slider" type="range" min="1000" max="60000" step="1000" value={delay} onChange={(e) => handleDelayChange(e)} />

      {online && src ? 
        <img 
          src={src} 
          alt="원격 게임 화면" 
          style={{ 
            display: 'block', 
            width: '100%', 
            height: '100%', 
            objectFit: 'contain',
            background: '#111' 
            }} /> 
            : <div style={{ 
                color: "#74829a",
                fontWeight: 700,
                width: "100%",
                height: "100%",
                alignContent: 'center',
                textAlign: 'center', 
              }}>
                <p>화면 대기 중</p>
                <p>{status}</p>
              </div>}
    </section>
  );
}
