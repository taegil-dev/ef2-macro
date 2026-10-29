import { Activity, Gamepad2, LogOut, Wifi, WifiOff } from "lucide-react";

export default function SideBar({ supabase, session, online, device }: { supabase: any; session: any; online: boolean; device: any }) {
    return (
        <aside className="sidebar">
            <div className="logo">
                <div className="brandMark small">
                    <Gamepad2 size={20} />
                </div>
                <span>Remote<span className="accent">Control.</span></span>
            </div>
            <div className="sideLabel">WORKSPACE</div>
            <div className="navActive">
                <Activity size={18} /> 대시보드
            </div>
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
    );
}