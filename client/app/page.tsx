"use client";
import { useCallback, useEffect, useState } from "react";
import { createClient, Session } from "@supabase/supabase-js";
import {
  MousePointerClick,
  Plug,
} from "lucide-react";
import LoginPage from "./login";
import { ClickTab, SwipeTab, MacroTab, GameScreen, Footer, RecentCommands } from "./components";
import SideBar from "./components/side-bar/SideBar";

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
);

type Device = {
  id: string;
  status: string;
  last_seen_at: string | null;
  last_error: string;
};

export type Command = {
  id: string;
  type: string;
  payload: any;
  status: string;
  error: string;
  created_at: string;
};

export default function Page() {
  const [session, setSession] = useState<Session | null>(null);
  const [message, setMessage] = useState("");
  const [device, setDevice] = useState<Device | null>(null);
  const [commands, setCommands] = useState<Command[]>([]);
  const [busy, setBusy] = useState(false);
  const [tab, setTab] = useState<"click" | "swipe" | "macro">("macro");

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => setSession(data.session));
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_e, s) => setSession(s));
    return () => subscription.unsubscribe();
  }, []);

  const api = useCallback(
    async (path: string, options?: RequestInit) => {
      const token = session?.access_token;
      if (!token) throw new Error("로그인이 필요합니다.");
      const response = await fetch(path, {
        ...options,
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
          ...options?.headers,
        },
        cache: "no-store",
      });
      const json = await response.json();
      if (!response.ok)
        throw new Error(json.error || `HTTP ${response.status}`);
      return json;
    },
    [session],
  );

  const refresh = useCallback(async () => {
    if (!session) return;
    try {
      const d = await api("/api/dashboard/status");
      setDevice(d.device);
      setCommands(d.commands);
    } catch (e) {
      setMessage((e as Error).message);
    }
  }, [api, session]);

  const online =
    !!device?.last_seen_at &&
    Date.now() - new Date(device.last_seen_at).getTime() < 45000;

  useEffect(() => {
    if (!session) {
      setDevice(null);
      setCommands([]);
      return;
    }

    if(online) {
      void refresh();
    }
    const timer = setInterval(() => {
      if(online) {
        void refresh();
      }
    }, 10000);

    return () => clearInterval(timer);
  }, [session, refresh, online]);

  const send = async (type: string, payload: Record<string, number> = {}) => {
    setBusy(true);
    setMessage("");
    try {
      await api("/api/dashboard/commands", {
        method: "POST",
        body: JSON.stringify({ type, payload }),
      });
      setMessage(`${type} 명령을 전송했어요.`);
      await refresh();
    } catch (e) {
      setMessage((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  if (!session)
    return <LoginPage supabase={supabase} message={message} setMessage={setMessage} />;
    
  return (
    <div className="appShell">
      <SideBar supabase={supabase} session={session} online={online} device={device} />
      <main className="main">
        <header className="topbar">
          <div>
            <span className="eyebrow">CONTROL CENTER</span>
            <h1>대시보드</h1>
            <p className="muted">PC 게임을 원격으로 관리하세요.</p>
          </div>
          <button className="outline refresh" onClick={refresh}>
            <Plug size={16} /> 연결
          </button>
        </header>
        <div className="content">
          <GameScreen supabase={supabase} deviceId={device?.id || ""} online={online} />
          <div className="columns">
            <section className="panel">
              <div className="panelHead">
                <div>
                  <h2>원격 제어</h2>
                  <p>좌표는 게임 화면 크기에 대한 비율입니다.</p>
                </div>
                <MousePointerClick size={20} />
              </div>
              <div className="tabs">
                <button
                  className={tab === "macro" ? "active" : ""}
                  onClick={() => setTab("macro")}
                >
                  매크로
                </button>
                <button
                  className={tab === "click" ? "active" : ""}
                  onClick={() => setTab("click")}
                >
                  클릭
                </button>
                <button
                  className={tab === "swipe" ? "active" : ""}
                  onClick={() => setTab("swipe")}
                >
                  스와이프
                </button>
              </div>
              {tab === "click" ? (
                <ClickTab send={send} busy={busy} online={online} />
              ) : tab === "swipe" ? (
                <SwipeTab send={send} busy={busy} online={online} />
              ) : (
                <MacroTab send={send} busy={busy} online={online} />
              )}
              {message && <p className="notice">{message}</p>}
            </section>
            <RecentCommands commands={commands} device={device} />
          </div>
        </div>
        <Footer />
      </main>
    </div>
  );
}