import { Play } from "lucide-react";
import { useEffect, useState } from "react";

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
                    <button
                        className="macroBtn"
                        disabled={busy || !online}
                        onClick={() => send("RUN_MACRO", { name: "환생", repeat: repeat })}
                    >
                        <Play size={17} />환생
                    </button>
                    <button
                        className="macroBtn"
                        disabled={busy || !online}
                        onClick={() => send("RUN_MACRO", { name: "영휴", repeat: repeat })}
                    >
                        <Play size={17} />영휴
                    </button>
                    <button
                        className="macroBtn"
                        disabled={busy || !online}
                        onClick={() => send("RUN_MACRO", { name: "테스트", repeat: repeat })}
                    >
                        <Play size={17} />테스트
                    </button>
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