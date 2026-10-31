import { Pause, Play } from "lucide-react";
import { useState } from "react";

export default function MacroTab({ send, busy, online }: { 
    send: (action: string, payload?: any) => void; 
    busy: boolean; 
    online: boolean 
}) {
    const [repeat, setRepeat] = useState(false);

    return (
        <>
            <div className="macroInputGrid">
                <div>
                    <label>저장된 다중 매크로</label>
                    <div className="macroList">
                        {[
                            "자동 환생", 
                            "테스트" 
                        ].map((macro) => (
                            <button
                                key={macro}
                                className="macroBtn"
                                disabled={busy || !online}
                                onClick={() => send("RUN_MULTI_MACRO", { name: macro, repeat: repeat })}
                            >
                                <Play size={17} />{macro}
                            </button>
                        ))}
                    </div>
                </div>
                <div>
                    <label>저장된 매크로</label>
                    <div className="macroList">
                        {[
                            "영입", 
                            "퀘스트 29 레벨업", 
                            "퀘스트 30 오픈", 
                            "퀘스트 30 레벨업", 
                            "웨이브 8000",
                            "웨이브 9000",
                            "테스트"
                        ].map((macro) => (
                            <button
                                key={macro}
                                className="macroBtn"
                                disabled={busy || !online}
                                onClick={() => send("RUN_MACRO", { name: macro, repeat: repeat })}
                            >
                                <Play size={17} />{macro}
                            </button>
                        ))}
                    </div>
                </div>
            </div>
            <div className="actionRow">
                <button
                    className="primary"
                    disabled={busy || !online} 
                    onClick={() => setRepeat(!repeat)}
                >
                    <Play size={17} /> 반복 실행
                    <span style={{ 
                        color: repeat ? "#4caf50" : "#ff9ea9",
                        backgroundColor: repeat ? "#2a4b31" : "#40232e",
                        borderColor: repeat ? "#2e5a2f" : "#6c3444",
                    }}>{repeat ? " ON" : " OFF"}</span>
                </button>
                <button
                  className="primary"
                  style={{ color: "#ff9ea9", backgroundColor: "#40232e", borderColor: "#6c3444" }}
                  disabled={busy || !online}
                  onClick={() => send("STOP")}
                >
                  <Pause size={18} /> 매크로 정지
                </button>
            </div>
        </>
    );
}