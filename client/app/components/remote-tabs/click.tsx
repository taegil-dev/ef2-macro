import { Play, MousePointerClick } from "lucide-react";
import { useState } from "react";

const clamp = (v: number) => Math.min(100, Math.max(0, v));

export default function ClickTab({ send, busy, online }: { 
    send: (action: string, payload?: any) => void; 
    busy: boolean; 
    online: boolean 
}) {
    const [x, setX] = useState(50);
    const [y, setY] = useState(50);
    const [interval, setIntervalValue] = useState(1);
    const [duration, setDuration] = useState(0.05);

    return (
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
                    disabled={busy || !online}
                    onClick={() =>
                        send("CLICK", { x: x / 100, y: y / 100, duration })
                    }
                >
                    <Play size={17} /> 클릭
                </button>
            </div>
        </>
    );
}