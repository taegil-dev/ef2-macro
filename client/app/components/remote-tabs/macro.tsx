import { Play } from "lucide-react";
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
                <label>저장된 매크로</label>
                <div className="macroList">
                    {[
                        "자동 환생", 
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
            <div className="actionRow">
                <input 
                    type="checkbox" 
                    id="macroLoop" 
                    disabled={busy || !online} 
                    checked={repeat}
                    onChange={() => setRepeat(!repeat)} />
                <label htmlFor="macroLoop">반복</label>
            </div>
        </>
    );
}