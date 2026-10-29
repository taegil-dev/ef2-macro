import { ArrowUpRight } from "lucide-react";
import { useState } from "react";

const clamp = (v: number) => Math.min(100, Math.max(0, v));

export default function SwipeTab({ send, busy, online }: { 
    send: (action: string, payload?: any) => void; 
    busy: boolean; 
    online: boolean 
}) {
    const [sx, setSx] = useState(20);
    const [sy, setSy] = useState(50);
    const [ex, setEx] = useState(80);
    const [ey, setEy] = useState(50);
    const [swipeDuration, setSwipeDuration] = useState(0.5);

    return (
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
                disabled={busy || !online}
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
    );
}