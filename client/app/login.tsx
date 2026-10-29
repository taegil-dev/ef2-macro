import { Gamepad2, LogIn, ShieldCheck } from "lucide-react";
import { useState } from "react";

export default function LoginPage({ supabase, message, setMessage }: { supabase: any; message: string; setMessage: (message: string) => void }) {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [authBusy, setAuthBusy] = useState(false);

    const login = async (e: React.SyntheticEvent<HTMLFormElement>) => {
        e.preventDefault();
        setAuthBusy(true);
        setMessage("");

        try {
            const { error } = await supabase.auth.signInWithPassword({
            email,
            password,
            });
            if (error) throw error;
        } catch (e) {
            setMessage((e as Error).message);
        } finally {
            setAuthBusy(false);
        }
    };
    
    return (
        <main className="loginWrap">
            <div className="loginCard">
                <div className="brandMark">
                    <Gamepad2 size={25} />
                </div>
                <div className="eyebrow">REMOTE CONTROL SYSTEM</div>
                <h1>
                    Macro<span>Deck.</span>
                </h1>
                <p className="muted">
                    언제 어디서나, 내 PC의 게임 매크로를 제어하세요.
                </p>
                <form onSubmit={login} className="loginForm">
                <label>
                    이메일
                    <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    required
                    />
                </label>
                <label>
                    비밀번호
                    <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                    />
                </label>
                <button className="primary" disabled={authBusy}>
                    <LogIn size={17} />
                    {authBusy ? "로그인 중..." : "로그인"}
                </button>
                </form>
                {message && <p className="notice error">{message}</p>}
                <div className="loginFoot">
                    <ShieldCheck size={15} /> Supabase Auth · 개인 전용 대시보드
                </div>
                <p className="hint">
                    첫 계정은 Supabase Authentication에서 생성하고, SQL의 기기 소유자로
                    등록하세요.
                </p>
            </div>
        </main>
    );
}