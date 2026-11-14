import { API_URL, OFFLINE } from "./config";
import type { DemoBundle, EventInfo, MetricRow, PondInfo, WsMsg } from "./types";

// eslint-disable-next-line @typescript-eslint/no-var-requires
const bundle: DemoBundle = require("./assets/demo.json");

async function get<T>(path: string): Promise<T> {
  const r = await fetch(`${API_URL}${path}`);
  if (!r.ok) throw new Error(`${r.status} ${await r.text()}`);
  return r.json();
}

export const loadPonds = async (): Promise<PondInfo[]> => {
  if (!OFFLINE) return get("/ponds");
  const avail = new Set(Object.keys(bundle.scenarios).map(k => k.split("|")[0]));
  return bundle.ponds.filter(p => avail.has(p.pond));
};
export const loadEvents = async (): Promise<EventInfo[]> => (OFFLINE ? bundle.events : get("/events"));
export const loadMetrics = async (): Promise<MetricRow[]> => (OFFLINE ? bundle.metrics : get("/metrics"));
export const offlinePrompts = (): string[] =>
  Object.keys(bundle.scenarios).filter(k => k.startsWith("prompt|")).map(k => k.slice(7));

export type RunRequest = { pond: string; prompt?: string; event?: string | null; intensity?: number; tickMs?: number };

/**
 * Start a run and stream messages. Live: WebSocket /ws/run. Offline: replays the bundled run with the same
 * message protocol, so the UI has a single code path. Returns a stop() function.
 */
export function startRun(req: RunRequest, onMsg: (m: WsMsg) => void): () => void {
  const tick = req.tickMs ?? 500;
  if (OFFLINE) {
    const key = req.prompt ? `prompt|${req.prompt}` : `${req.pond}|${req.event ?? "none"}`;
    const run = bundle.scenarios[key] ?? bundle.scenarios[`${req.pond}|none`];
    if (!run) { onMsg({ type: "error", detail: `Bản offline không có kịch bản ${key}` }); return () => {}; }
    const scenario = run.scenario ?? { title: req.event ?? "Bình thường", narrative: "", events: [] };
    onMsg({ type: "scenario", scenario, source: run.source ?? "offline", pond: run.pond,
            start_index: run.start_index, step_minutes: run.step_minutes, total: run.points.length });
    const begin = Math.max(0, (run.start_index ?? 0) - 18);
    onMsg({ type: "history", points: run.points.slice(0, begin) });
    let i = begin;
    const t = setInterval(() => {
      if (i >= run.points.length) { clearInterval(t); onMsg({ type: "end", summary: run.summary }); return; }
      onMsg({ type: "point", i, point: run.points[i] }); i++;
    }, tick);
    return () => clearInterval(t);
  }
  const ws = new WebSocket(`${API_URL.replace(/^http/, "ws")}/ws/run`);
  let closed = false;
  ws.onopen = () => ws.send(JSON.stringify({ pond: req.pond, prompt: req.prompt, event: req.event,
                                             intensity: req.intensity, tick_ms: tick }));
  ws.onmessage = e => onMsg(JSON.parse(String(e.data)) as WsMsg);
  ws.onerror = () => { if (!closed) onMsg({ type: "error", detail: `Không kết nối được ${API_URL}` }); };
  return () => { closed = true; ws.close(); };
}
