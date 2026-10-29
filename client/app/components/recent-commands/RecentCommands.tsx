import { Send, CircleHelp, Pause, ArrowDownRight, Play } from "lucide-react";

type Command = {
  id: string;
  type: string;
  payload: any;
  status: string;
  error: string;
  created_at: string;
};

export default function RecentCommands({ commands, device }: { commands: Command[], device: any }) {
    return (
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
                                        <Play size={17} />
                                    )}
                                </div>
                                <div className="historyText">
                                    <strong>
                                        {(
                                            {
                                                CLICK: "1회 클릭",
                                                STOP: "매크로 정지",
                                                SWIPE: "스와이프",
                                                RUN_MACRO: c.payload?.name ? ` ${c.payload.name}` : "",
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
    );
}