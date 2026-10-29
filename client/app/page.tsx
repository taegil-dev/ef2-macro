"use Client";
import { useCallback, useEffect, useState } from "react";
import { createClient, Session } from "@supabase/supabase-js";
import {
  Activity,
  ArrowDownRight,
  ArrowUpRight,
  Check,
  CircleHelp,
  Clock3,
  Gamepad2,
  LogIn,
  LogOut,
  MousePointerClick,
  Pause,
  Play,
  RefreshCw,
  Send,
  ShieldCheck,
  Smartphone,
  Wifi,
  WifiOff,
} from "lucide-react";
import LoginPage from "./login";

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

type Command = {
  id: string;
  type: string;
  status: string;
  error: string;
  created_at: string;
};

const clamp = (v: number) => Math.min(100, Math.max(0, v));

export default function Page() {
  const [session, setSession] = useState<Session | null>(null);
  const [message, setMessage] = useState("");
  const [device, setDevice] = useState<Device | null>(null);
  const [commands, setCommands] = useState<Command[]>([]);
  const [x, setX] = useState(50);
  const [y, setY] = useState(50);
  const [sx, setSx] = useState(20);
  const [sy, setSy] = useState(50);
  const [ex, setEx] = useState(80);
  const [ey, setEy] = useState(50);
  const [interval, setIntervalValue] = useState(1);
  const [duration, setDuration] = useState(0.05);
  const [swipeDuration, setSwipeDuration] = useState(0.5);
  const [busy, setBusy] = useState(false);
  const [tab, setTab] = useState<"click" | "swipe">("click");

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

  useEffect(() => {
    if (!session) {
      setDevice(null);
      setCommands([]);
      return;
    }
    refresh();
    const timer = setInterval(refresh, 4000);
    return () => clearInterval(timer);
  }, [session, refresh]);

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

  const online =
    !!device?.last_seen_at &&
    Date.now() - new Date(device.last_seen_at).getTime() < 45000;

  if (!session)
    return <LoginPage supabase={supabase} message={message} setMessage={setMessage} />;
    
  return (
    <div className="appShell">
      <aside className="sidebar">
        <div className="logo">
          <div className="brandMark small">
            <Gamepad2 size={20} />
          </div>
          <span>
            Remote<span className="accent">Control.</span>
          </span>
        </div>
        <div className="sideLabel">WORKSPACE</div>
        <div className="navActive">
          <Activity size={18} /> 대시보드
        </div>
        <div className="sideBottom">
          <div className="userAvatar">
            {session.user.email?.[0]?.toUpperCase() || "U"}
          </div>
          <div className="userInfo">
            <strong>내 계정</strong>
            <small>{session.user.email}</small>
          </div>
          <button
            className="iconBtn"
            title="로그아웃"
            onClick={() => supabase.auth.signOut()}
          >
            <LogOut size={17} />
          </button>
        </div>
      </aside>
      <main className="main">
        <header className="topbar">
          <div>
            <span className="eyebrow">CONTROL CENTER</span>
            <h1>대시보드</h1>
            <p className="muted">PC 게임을 원격으로 관리하세요.</p>
          </div>
          <button className="outline refresh" onClick={refresh}>
            <RefreshCw size={16} /> 새로고침
          </button>
        </header>
        <div className="content">
          <div className="statusGrid">
            <section className="statCard">
              <div className="statTop">
                <span>PC 연결 상태</span>
                {online ? (
                  <Wifi size={19} className="green" />
                ) : (
                  <WifiOff size={19} />
                )}
              </div>
              <strong className={online ? "green" : ""}>
                {online ? "온라인" : "오프라인"}
              </strong>
              <small>{device?.id || "등록된 PC 확인 중"}</small>
            </section>
            <section className="statCard">
              <div className="statTop">
                <span>매크로 상태</span>
                <Activity size={19} />
              </div>
              <strong>
                {!online
                  ? "연결 대기"
                  : device?.status === "running"
                    ? "실행 중"
                    : "대기 중"}
              </strong>
              <small>마지막 보고 기준</small>
            </section>
            <section className="statCard">
              <div className="statTop">
                <span>마지막 연결</span>
                <Clock3 size={19} />
              </div>
              <strong className="dateStat">
                {device?.last_seen_at
                  ? new Date(device.last_seen_at).toLocaleTimeString("ko-KR")
                  : "—"}
              </strong>
              <small>
                {device?.last_seen_at
                  ? new Date(device.last_seen_at).toLocaleDateString("ko-KR")
                  : "기록 없음"}
              </small>
            </section>
          </div>
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
                <>
                  <div className="preview" aria-label="클릭 좌표 미리보기">
                    <div className="gridlines" />
                    <div
                      className="point"
                      style={{ left: `${x}%`, top: `${y}%` }}
                    />
                    <span className="previewCaption">TARGET POSITION</span>
                  </div>
                  <div className="inputGrid">
                    <label>
                      가로 X (%)
                      <input
                        type="number"
                        min="0"
                        max="100"
                        value={x}
                        onChange={(e) => setX(clamp(+e.target.value))}
                      />
                    </label>
                    <label>
                      세로 Y (%)
                      <input
                        type="number"
                        min="0"
                        max="100"
                        value={y}
                        onChange={(e) => setY(clamp(+e.target.value))}
                      />
                    </label>
                    <label>
                      반복 간격 (초)
                      <input
                        type="number"
                        min="0.1"
                        max="3600"
                        step="0.1"
                        value={interval}
                        onChange={(e) => setIntervalValue(+e.target.value)}
                      />
                    </label>
                    <label>
                      누르는 시간 (초)
                      <input
                        type="number"
                        min="0.01"
                        max="0.5"
                        step="0.01"
                        value={duration}
                        onChange={(e) => setDuration(+e.target.value)}
                      />
                    </label>
                  </div>
                  <div className="actionRow">
                    <button
                      className="primary"
                      disabled={busy}
                      onClick={() =>
                        send("START_REPEAT", {
                          x: x / 100,
                          y: y / 100,
                          interval,
                          duration,
                        })
                      }
                    >
                      <Play size={17} /> 반복 시작
                    </button>
                    <button
                      className="outline"
                      disabled={busy}
                      onClick={() =>
                        send("CLICK", { x: x / 100, y: y / 100, duration })
                      }
                    >
                      <MousePointerClick size={17} /> 1회 클릭
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <div className="preview">
                    <div className="gridlines" />
                    <svg
                      className="swipeLine"
                      viewBox="0 0 100 100"
                      preserveAspectRatio="none"
                    >
                      <line
                        x1={sx}
                        y1={sy}
                        x2={ex}
                        y2={ey}
                        stroke="#7c89ff"
                        strokeWidth="1.2"
                      />
                      <circle cx={sx} cy={sy} r="2" fill="#a4adff" />
                      <circle cx={ex} cy={ey} r="2" fill="#34d399" />
                    </svg>
                    <span className="previewCaption">SWIPE PATH</span>
                  </div>
                  <div className="inputGrid">
                    {[
                      ["시작 X (%)", sx, setSx],
                      ["시작 Y (%)", sy, setSy],
                      ["끝 X (%)", ex, setEx],
                      ["끝 Y (%)", ey, setEy],
                    ].map(([label, val, setter]) => (
                      <label key={String(label)}>
                        {String(label)}
                        <input
                          type="number"
                          min="0"
                          max="100"
                          value={val as number}
                          onChange={(e) =>
                            (setter as (v: number) => void)(
                              clamp(+e.target.value),
                            )
                          }
                        />
                      </label>
                    ))}
                    <label>
                      이동 시간 (초)
                      <input
                        type="number"
                        min="0.05"
                        max="5"
                        step="0.05"
                        value={swipeDuration}
                        onChange={(e) => setSwipeDuration(+e.target.value)}
                      />
                    </label>
                  </div>
                  <button
                    className="primary wide"
                    disabled={busy}
                    onClick={() =>
                      send("SWIPE", {
                        start_x: sx / 100,
                        start_y: sy / 100,
                        end_x: ex / 100,
                        end_y: ey / 100,
                        duration: swipeDuration,
                        steps: 30,
                      })
                    }
                  >
                    <ArrowUpRight size={17} /> 스와이프 실행
                  </button>
                </>
              )}
              <button
                className="stopBtn"
                disabled={busy}
                onClick={() => send("STOP")}
              >
                <Pause size={18} /> 매크로 정지
              </button>
              {message && <p className="notice">{message}</p>}
            </section>
            <section className="panel history">
              <div className="panelHead">
                <div>
                  <h2>최근 명령</h2>
                  <p>PC Agent에서 처리한 명령 내역</p>
                </div>
                <Send size={19} />
              </div>
              {commands.length === 0 ? (
                <div className="empty">
                  <CircleHelp size={30} />
                  <p>아직 전송한 명령이 없습니다.</p>
                </div>
              ) : (
                <div className="historyList">
                  {commands.map((c) => (
                    <div className="historyItem" key={c.id}>
                      <div className="historyIcon">
                        {c.type === "STOP" ? (
                          <Pause size={17} />
                        ) : c.type === "SWIPE" ? (
                          <ArrowDownRight size={17} />
                        ) : (
                          <MousePointerClick size={17} />
                        )}
                      </div>
                      <div className="historyText">
                        <strong>
                          {(
                            {
                              CLICK: "1회 클릭",
                              START_REPEAT: "반복 클릭 시작",
                              STOP: "매크로 정지",
                              SWIPE: "스와이프",
                            } as Record<string, string>
                          )[c.type] || c.type}
                        </strong>
                        <small>
                          {new Date(c.created_at).toLocaleString("ko-KR")}
                          {c.error ? ` · ${c.error}` : ""}
                        </small>
                      </div>
                      <span className={`pill ${c.status}`}>
                        {(
                          {
                            pending: "대기",
                            claimed: "전달됨",
                            done: "처리됨",
                            failed: "실패",
                            expired: "만료",
                          } as Record<string, string>
                        )[c.status] || c.status}
                      </span>
                    </div>
                  ))}
                </div>
              )}
              {device?.last_error && (
                <p className="notice error">PC 오류: {device.last_error}</p>
              )}
            </section>
          </div>
          <footer>
            <ShieldCheck size={15} /> 암호화된 HTTPS API · 개인 PC 전용{" "}
            <span>MacroDeck v1.0</span>
          </footer>
        </div>
      </main>
    </div>
  );
}
