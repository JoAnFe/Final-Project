import { useEffect, useState } from "react";
import { token, listAlerts, listDevices, readings } from "./api";

const glitch = (text: string) => text.split("").map((char, idx) => (
  <span
    key={`${char}-${idx}`}
    className="animate-[pulse_3s_ease-in-out_infinite]"
    style={{ animationDelay: `${idx * 45}ms` }}
  >
    {char}
  </span>
));

const cardClasses =
  "bg-gradient-to-br from-emerald-900/60 via-slate-900/80 to-cyan-900/60 border border-emerald-500/30 shadow-lg shadow-emerald-900/40 rounded-xl backdrop-blur transition-transform hover:-translate-y-1";

const gridLabel = "text-xs uppercase tracking-[0.3em] text-emerald-300/80 mb-2";

export default function App() {
  const [tok, setTok] = useState<string>("");
  const [alerts, setAlerts] = useState<any[]>([]);
  const [devices, setDevices] = useState<any[]>([]);
  const [sel, setSel] = useState<string>("");
  const [data, setData] = useState<any[]>([]);

  useEffect(() => { token().then(setTok); }, []);
  useEffect(() => { if (tok) { listDevices(tok).then(setDevices); listAlerts(tok).then(setAlerts); }}, [tok]);
  useEffect(() => { if (tok && sel) readings(tok, sel).then(setData); }, [tok, sel]);

  return (
    <div className="min-h-screen bg-[#050b0f] text-emerald-200 font-mono">
      <div className="mx-auto max-w-6xl px-6 py-10">
        <header className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl md:text-4xl font-semibold text-cyan-200 drop-shadow-glow">{glitch("SMART AG COMMAND")}</h1>
            <p className="text-sm text-emerald-400/70">Telemetry ops console · encrypted uplink · status: <span className="text-cyan-300">ONLINE</span></p>
          </div>
          <div className="flex items-center gap-3 text-xs">
            <span className="h-2 w-2 animate-ping rounded-full bg-emerald-400" />
            <span className="text-emerald-300/80">MQTT/8883</span>
            <span className="text-cyan-300/80">DB/3306</span>
          </div>
        </header>

        <section className="mt-8 grid gap-6 md:grid-cols-[260px_1fr]">
          <div className={`${cardClasses} p-4`}> 
            <p className={gridLabel}>Device Channel</p>
            <select
              className="w-full rounded bg-slate-900/80 border border-emerald-500/40 px-3 py-2 text-sm text-emerald-200 focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400"
              onChange={e => setSel(e.target.value)}
              value={sel}
            >
              <option value="">Select device</option>
              {devices.map((d: any) => (
                <option key={d.device_id} value={d.device_id}>
                  {d.common_name} ({d.device_id})
                </option>
              ))}
            </select>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <div className={`${cardClasses} p-5`}> 
              <h2 className={gridLabel}>Latest Telemetry</h2>
              <div className="space-y-2 text-sm">
                {data.slice(-10).map((r: any, i: number) => (
                  <div key={i} className="flex flex-wrap items-baseline gap-4 rounded border border-emerald-500/10 bg-slate-900/60 px-3 py-2">
                    <span className="text-xs text-emerald-300/70">{new Date(r.ts).toLocaleTimeString()}</span>
                    <span className="text-emerald-200">T:{r.t?.toFixed?.(1)}°C</span>
                    <span className="text-cyan-200">H:{r.h?.toFixed?.(0)}%</span>
                    <span className="text-emerald-300">SM:{(r.sm * 100)?.toFixed?.(0)}%</span>
                    <span className="text-cyan-300">pH:{r.ph?.toFixed?.(2)}</span>
                  </div>
                ))}
                {data.length === 0 && (
                  <p className="text-emerald-300/60">Awaiting uplink…</p>
                )}
              </div>
            </div>

            <div className={`${cardClasses} p-5`}> 
              <h2 className={gridLabel}>Active Alerts</h2>
              <div className="space-y-2 text-sm">
                {alerts.map((a: any, i: number) => (
                  <div key={i} className="rounded border border-cyan-500/20 bg-slate-900/60 px-3 py-2">
                    <div className="flex justify-between text-xs text-cyan-300/70">
                      <span>{a.device_id}</span>
                      <span>{a.rule}</span>
                    </div>
                    <div className="mt-1 text-emerald-100">
                      <span className="mr-2 inline-flex items-center gap-1 text-[11px] uppercase tracking-widest text-cyan-400">
                        <span className="h-1.5 w-1.5 rounded-full bg-cyan-400" />
                        {a.severity?.toUpperCase?.() ?? a.sev?.toUpperCase?.()}
                      </span>
                      {a.message ?? a.msg}
                    </div>
                  </div>
                ))}
                {alerts.length === 0 && (
                  <p className="text-cyan-300/60">No anomalies detected.</p>
                )}
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
