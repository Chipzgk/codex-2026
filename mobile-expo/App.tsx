import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { SafeAreaView, ScrollView, Text, View, Pressable, StyleSheet, useWindowDimensions,
         ActivityIndicator, TextInput, Animated } from "react-native";
import Svg, { Polyline, Line, Rect, Text as SvgText } from "react-native-svg";
import { OFFLINE } from "./config";
import { loadEvents, loadMetrics, loadPonds, offlinePrompts, startRun } from "./api";
import { initNotifications, notify } from "./notify";
import type { Alert, EventInfo, MetricRow, PondInfo, Point, Scenario, Summary, WsMsg } from "./types";

const C = { ink: "#14213d", muted: "#6b7280", bg: "#f4f6f8", card: "#ffffff", line: "#e5e7eb",
  SAFE: "#2a9d8f", WATCH: "#d4a017", DANGER: "#e63946", SENSOR: "#f08a24", do: "#1d4e89" };
const WINDOW = 72;  // 12 h at 10-min steps
const INTENSITY = [{ v: 0.6, label: "Nhẹ" }, { v: 1.0, label: "Vừa" }, { v: 1.4, label: "Nặng" }];
const SAMPLE_PROMPTS = [
  "3 giờ sáng mất điện, máy sục khí ngừng chạy",
  "Trời âm u mấy ngày, tảo tàn, nước đục",
  "Chiều có sấm sét làm cảm biến nhiễu, đêm máy sục khí hỏng",
];
const ALERT_COLOR: Record<Alert["kind"], string> = { watch: C.WATCH, danger: C.DANGER, sensor: C.SENSOR, resolved: C.SAFE };

function status(p: Point) {
  if (p.flags.sensor_check) return { text: "KIỂM TRA CẢM BIẾN", color: C.SENSOR };
  if (p.flags.danger) return { text: "NGUY HIỂM", color: C.DANGER };
  if (p.flags.watch) return { text: "CẦN THEO DÕI", color: C.WATCH };
  return { text: "AN TOÀN", color: C.SAFE };
}

function Chart({ pts, firstIndex, eventStart, width }: { pts: Point[]; firstIndex: number; eventStart: number | null; width: number }) {
  const h = 150, padL = 26, w = width - padL;
  const vals = pts.map(p => p.do ?? 0);
  const max = Math.max(10, ...vals);
  const x = (i: number) => padL + (i / Math.max(1, WINDOW - 1)) * w;
  const y = (v: number) => h - (Math.min(v, max) / max) * h;
  const evX = eventStart !== null && eventStart >= firstIndex && eventStart < firstIndex + pts.length ? x(eventStart - firstIndex) : null;
  return (
    <Svg width={width} height={h + 4}>
      <Rect x={padL} y={y(3)} width={w} height={h - y(3)} fill="#e6394618" />
      <Line x1={padL} x2={width} y1={y(3)} y2={y(3)} stroke={C.DANGER} strokeDasharray="4 4" strokeWidth={1} />
      <SvgText x={0} y={y(3) + 4} fontSize={10} fill={C.DANGER}>3</SvgText>
      <SvgText x={0} y={y(max) + 10} fontSize={10} fill={C.muted}>{max.toFixed(0)}</SvgText>
      {pts.map((p, i) => p.flags.sensor_check
        ? <Rect key={i} x={x(i) - w / WINDOW / 2} y={0} width={w / WINDOW} height={h} fill="#f08a2422" /> : null)}
      {evX !== null && <Line x1={evX} x2={evX} y1={0} y2={h} stroke={C.ink} strokeDasharray="2 3" />}
      <Polyline points={vals.map((v, i) => `${x(i)},${y(v)}`).join(" ")} fill="none" stroke={C.do} strokeWidth={2} />
    </Svg>
  );
}

function Chip({ label, on, onPress, tone }: { label: string; on?: boolean; onPress: () => void; tone?: string }) {
  return (
    <Pressable onPress={onPress} style={[s.chip, on && { backgroundColor: tone ?? C.ink, borderColor: tone ?? C.ink }]}>
      <Text style={[s.chipTxt, on && { color: "white" }]}>{label}</Text>
    </Pressable>
  );
}

/** In-app banner that slides in for each alert (works on web too, where OS notifications are not used). */
function Toast({ alert, onHide }: { alert: Alert | null; onHide: () => void }) {
  const y = useRef(new Animated.Value(-140)).current;
  useEffect(() => {
    if (!alert) return;
    Animated.sequence([
      Animated.spring(y, { toValue: 0, useNativeDriver: true }),
      Animated.delay(alert.severity >= 2 ? 4500 : 3000),
      Animated.timing(y, { toValue: -140, duration: 250, useNativeDriver: true }),
    ]).start(() => onHide());
  }, [alert]);
  if (!alert) return null;
  return (
    <Animated.View style={[s.toast, { borderLeftColor: ALERT_COLOR[alert.kind], transform: [{ translateY: y }] }]}>
      <Text style={[s.toastTitle, { color: ALERT_COLOR[alert.kind] }]}>🔔 {alert.title}</Text>
      <Text style={s.toastBody}>{alert.body}</Text>
    </Animated.View>
  );
}

type Mode = "prompt" | "manual";

export default function App() {
  const { width } = useWindowDimensions();
  const [ponds, setPonds] = useState<PondInfo[]>([]);
  const [events, setEvents] = useState<EventInfo[]>([]);
  const [metrics, setMetrics] = useState<MetricRow[]>([]);
  const [pond, setPond] = useState("");
  const [mode, setMode] = useState<Mode>("prompt");
  const [prompt, setPrompt] = useState(SAMPLE_PROMPTS[0]);
  const [event, setEvent] = useState<string | null>(null);
  const [intensity, setIntensity] = useState(1.0);

  const [pts, setPts] = useState<Point[]>([]);
  const [meta, setMeta] = useState<{ scenario: Scenario; source: string; start: number | null; step: number } | null>(null);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [running, setRunning] = useState(false);
  const [statusText, setStatusText] = useState("");
  const [err, setErr] = useState("");
  const [toast, setToast] = useState<Alert | null>(null);
  const [feed, setFeed] = useState<(Alert & { time: string })[]>([]);
  const stopRef = useRef<() => void>(() => {});
  const prompts = OFFLINE ? offlinePrompts() : SAMPLE_PROMPTS;

  useEffect(() => {
    initNotifications().catch(() => {});
    Promise.all([loadPonds(), loadEvents(), loadMetrics()])
      .then(([p, e, m]) => { setPonds(p); setEvents(e); setMetrics(m); setPond(p.find(x => !x.showcase)?.pond ?? p[0]?.pond ?? ""); })
      .catch(e => setErr(String(e)));
    if (OFFLINE) setPrompt(offlinePrompts()[0] ?? "");
    return () => stopRef.current();
  }, []);

  const onMsg = useCallback((m: WsMsg) => {
    switch (m.type) {
      case "status": setStatusText(m.text); break;
      case "scenario": setMeta({ scenario: m.scenario, source: m.source, start: m.start_index, step: m.step_minutes }); setStatusText(""); break;
      case "history": setPts(m.points); break;
      case "point":
        setPts(prev => [...prev, m.point]);
        if (m.point.alert) {
          const a = m.point.alert;
          setToast(a); setFeed(f => [{ ...a, time: m.point.time }, ...f].slice(0, 20));
          notify(a).catch(() => {});
        }
        break;
      case "end": setSummary(m.summary); setRunning(false); break;
      case "error": setErr(m.detail); setRunning(false); setStatusText(""); break;
    }
  }, []);

  const run = useCallback(() => {
    if (!pond) return;
    stopRef.current();
    setPts([]); setMeta(null); setSummary(null); setFeed([]); setErr(""); setRunning(true);
    const showcase = ponds.find(p => p.pond === pond)?.showcase;
    stopRef.current = startRun(
      showcase ? { pond } : mode === "prompt" ? { pond, prompt } : { pond, event, intensity }, onMsg);
  }, [pond, ponds, mode, prompt, event, intensity, onMsg]);

  const stop = () => { stopRef.current(); setRunning(false); };

  const view = useMemo(() => {
    if (!pts.length) return null;
    const firstIndex = Math.max(0, pts.length - WINDOW);
    return { pts: pts.slice(firstIndex), firstIndex, cur: pts[pts.length - 1] };
  }, [pts]);

  const firstSeen = (cond: (p: Point) => boolean) => {
    if (!meta) return "—";
    const start = meta.start ?? 0;
    const i = pts.findIndex((p, k) => k >= start && cond(p));
    return i < 0 ? "—" : `+${(i - start) * meta.step} phút`;
  };
  const showcase = ponds.find(p => p.pond === pond)?.showcase;

  return (
    <SafeAreaView style={s.root}>
      <Toast alert={toast} onHide={() => setToast(null)} />
      <ScrollView contentContainerStyle={s.wrap}>
        <View style={s.header}>
          <Text style={s.h1}>PondGuard</Text>
          <Text style={[s.badge, { backgroundColor: OFFLINE ? "#e5e7eb" : "#d1fae5" }]}>{OFFLINE ? "Offline" : "Live"}</Text>
        </View>
        <Text style={s.sub}>Dữ liệu cảm biến thật · sự cố do AI/ người dùng giả lập</Text>
        {err ? <Text style={s.err}>{err}</Text> : null}

        <Text style={s.label}>Ao</Text>
        <View style={s.row}>{ponds.map(p => (
          <Chip key={p.pond} label={p.showcase ? `${p.pond} · cảm biến lỗi thật` : p.pond} on={p.pond === pond}
            tone={p.showcase ? C.SENSOR : undefined} onPress={() => setPond(p.pond)} />))}</View>

        {!showcase && <>
          <View style={[s.row, { marginTop: 12 }]}>
            <Chip label="✨ Mô tả tình huống (AI)" on={mode === "prompt"} onPress={() => setMode("prompt")} />
            <Chip label="Chọn sự cố" on={mode === "manual"} onPress={() => setMode("manual")} />
          </View>
          {mode === "prompt" ? <>
            {!OFFLINE && <TextInput style={s.input} value={prompt} onChangeText={setPrompt} multiline
              placeholder="Ví dụ: 3 giờ sáng mất điện, máy sục khí ngừng" placeholderTextColor={C.muted} />}
            <View style={[s.row, { marginTop: 8 }]}>{prompts.map(p => (
              <Chip key={p} label={p} on={prompt === p} onPress={() => setPrompt(p)} />))}</View>
          </> : <>
            <View style={[s.row, { marginTop: 8 }]}>
              <Chip label="Bình thường" on={event === null} onPress={() => setEvent(null)} />
              {events.map(e => <Chip key={e.id} label={e.label} on={event === e.id}
                tone={e.kind === "risk" ? C.DANGER : C.SENSOR} onPress={() => setEvent(e.id)} />)}
            </View>
            {!OFFLINE && <View style={[s.row, { marginTop: 8 }]}>{INTENSITY.map(o =>
              <Chip key={o.v} label={`Cường độ: ${o.label}`} on={intensity === o.v} onPress={() => setIntensity(o.v)} />)}</View>}
          </>}
        </>}

        <View style={[s.row, { marginTop: 12 }]}>
          <Pressable style={s.primary} onPress={run}>
            {running && !view ? <ActivityIndicator color="white" /> : <Text style={s.primaryTxt}>▶ Chạy real-time</Text>}
          </Pressable>
          {running && <Pressable style={s.secondary} onPress={stop}><Text style={s.secondaryTxt}>Dừng</Text></Pressable>}
        </View>
        {statusText ? <Text style={s.small}>{statusText}</Text> : null}

        {meta && meta.scenario.events.length > 0 && (
          <View style={s.scenario}>
            <Text style={s.cmpHead}>{meta.scenario.title}</Text>
            {meta.scenario.narrative ? <Text style={s.meta}>{meta.scenario.narrative}</Text> : null}
            <Text style={s.small}>
              {meta.source === "llm" ? "Kịch bản do LLM viết" : meta.source.startsWith("fallback") ? "Kịch bản mẫu (không gọi được LLM)" : meta.source === "offline" ? "Bản offline" : "Kịch bản chọn tay"}
              {" · "}{meta.scenario.events.map(e => `${events.find(x => x.id === e.type)?.label ?? e.type} lúc ${e.start_hour}h`).join(", ")}
            </Text>
          </View>
        )}

        {view && (() => {
          const st = status(view.cur);
          return <>
            <View style={[s.card, { borderColor: st.color }]}>
              <View style={s.flagRow}>
                <Text style={s.small}>{new Date(view.cur.time).toLocaleString("vi-VN")}</Text>
                <View style={s.row}>
                  {view.cur.flags.watch && <Text style={[s.flag, { backgroundColor: C.WATCH }]}>WATCH</Text>}
                  {view.cur.flags.danger && <Text style={[s.flag, { backgroundColor: C.DANGER }]}>DANGER</Text>}
                  {view.cur.flags.sensor_check && <Text style={[s.flag, { backgroundColor: C.SENSOR }]}>SENSOR</Text>}
                </View>
              </View>
              <Text style={[s.big, { color: st.color }]}>{st.text}</Text>
              <Text style={s.risk}>Điểm rủi ro {view.cur.risk.toFixed(0)}/100</Text>
              <Text style={s.meta}>DO {view.cur.do?.toFixed(1) ?? "—"} mg/L · bất thường {(view.cur.anomaly * 100).toFixed(0)}% · tin cậy {(view.cur.reliability * 100).toFixed(0)}%</Text>
              {view.cur.reasons.map((r, i) => <Text key={i} style={s.reason}>• {r}</Text>)}
              <Text style={[s.action, { color: st.color }]}>→ {view.cur.action}</Text>
            </View>

            <Text style={s.label}>DO 12 giờ gần nhất · vùng đỏ &lt; 3 mg/L · cam: dữ liệu không đáng tin</Text>
            <View style={s.chartBox}><Chart pts={view.pts} firstIndex={view.firstIndex} eventStart={meta?.start ?? null} width={width - 56} /></View>

            <View style={s.cmp}>
              <View style={s.cmpCol}>
                <Text style={s.cmpHead}>Ngưỡng cố định</Text>
                <Text style={[s.cmpNow, { color: view.cur.threshold_alert ? C.DANGER : C.SAFE }]}>{view.cur.threshold_alert ? "BÁO ĐỘNG" : "im lặng"}</Text>
                <Text style={s.small}>Báo lần đầu: {firstSeen(p => p.threshold_alert)}</Text>
              </View>
              <View style={s.cmpCol}>
                <Text style={s.cmpHead}>PondGuard</Text>
                <Text style={[s.cmpNow, { color: st.color }]}>{st.text.toLowerCase()}</Text>
                <Text style={s.small}>Nguy hiểm: {firstSeen(p => p.flags.danger)}</Text>
                <Text style={s.small}>Kiểm tra cảm biến: {firstSeen(p => p.flags.sensor_check)}</Text>
              </View>
            </View>
            {view.cur.event ? <Text style={s.truth}>Sự thật (chỉ để trình diễn): {events.find(e => e.id === view.cur.event)?.label ?? view.cur.event}</Text> : null}
          </>;
        })()}

        {feed.length > 0 && <View style={s.metrics}>
          <Text style={s.cmpHead}>Thông báo đã gửi ({feed.length})</Text>
          {feed.map((a, i) => (
            <View key={i} style={[s.feedItem, { borderLeftColor: ALERT_COLOR[a.kind] }]}>
              <Text style={s.small}>{new Date(a.time).toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" })}</Text>
              <Text style={[s.feedTitle, { color: ALERT_COLOR[a.kind] }]}>{a.title}</Text>
              <Text style={s.reason}>{a.body}</Text>
            </View>))}
        </View>}

        {summary && <Text style={s.small}>Kết thúc kịch bản.</Text>}

        {metrics.length > 0 && <View style={s.metrics}>
          <Text style={s.cmpHead}>Kết quả đánh giá (dữ liệu thật + sự cố chèn có nhãn, trung bình 5 seed giữ riêng)</Text>
          <View style={s.mRow}>{["", "F1", "Báo giả/ngày", "Lỗi CB→nguy hiểm"].map(h => <Text key={h} style={[s.mCell, s.mHead]}>{h}</Text>)}</View>
          {metrics.filter(m => m.method !== "iforest").map(m => (
            <View key={m.method} style={s.mRow}>
              <Text style={[s.mCell, { fontWeight: "600" }]}>{{ threshold: "Ngưỡng", fuzzy_only: "Fuzzy", hybrid: "Hybrid" }[m.method] ?? m.method}</Text>
              <Text style={s.mCell}>{m.f1.toFixed(2)}</Text>
              <Text style={s.mCell}>{m.false_alarms_per_day.toFixed(1)}</Text>
              <Text style={s.mCell}>{m.sensor_faults_raised_as_danger}</Text>
            </View>))}
        </View>}
      </ScrollView>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  root: { flex: 1, backgroundColor: C.bg }, wrap: { padding: 16, paddingBottom: 48 },
  header: { flexDirection: "row", alignItems: "center", justifyContent: "space-between" },
  h1: { fontSize: 28, fontWeight: "800", color: C.ink }, sub: { color: C.muted, marginBottom: 4 },
  badge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 10, overflow: "hidden", fontSize: 12, color: C.ink },
  err: { color: C.DANGER, marginVertical: 6 },
  label: { color: C.muted, marginTop: 12, marginBottom: 6, fontSize: 13 },
  row: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  chip: { paddingHorizontal: 12, paddingVertical: 7, borderRadius: 16, backgroundColor: C.card, borderWidth: 1, borderColor: C.line },
  chipTxt: { color: C.ink, fontSize: 13 },
  input: { backgroundColor: C.card, borderRadius: 12, borderWidth: 1, borderColor: C.line, padding: 12, marginTop: 8, color: C.ink, minHeight: 60 },
  primary: { backgroundColor: C.ink, paddingHorizontal: 18, paddingVertical: 11, borderRadius: 12, minWidth: 160, alignItems: "center" },
  primaryTxt: { color: "white", fontWeight: "700" },
  secondary: { paddingHorizontal: 16, paddingVertical: 11, borderRadius: 12, borderWidth: 1, borderColor: C.ink },
  secondaryTxt: { color: C.ink, fontWeight: "600" },
  scenario: { backgroundColor: "#eef2ff", borderRadius: 12, padding: 12, marginTop: 12, gap: 4 },
  card: { borderWidth: 3, borderRadius: 16, padding: 16, backgroundColor: C.card, marginTop: 16, gap: 4 },
  flagRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  flag: { color: "white", fontSize: 10, fontWeight: "800", paddingHorizontal: 6, paddingVertical: 2, borderRadius: 6, overflow: "hidden" },
  big: { fontSize: 28, fontWeight: "900" }, risk: { fontSize: 18, fontWeight: "700", color: C.ink },
  meta: { color: C.ink }, reason: { color: C.ink }, action: { marginTop: 6, fontWeight: "800", fontSize: 15 },
  small: { color: C.muted, fontSize: 12 },
  chartBox: { backgroundColor: C.card, borderRadius: 12, padding: 12 },
  cmp: { flexDirection: "row", gap: 10, marginTop: 12 },
  cmpCol: { flex: 1, backgroundColor: C.card, borderRadius: 12, padding: 12, gap: 2 },
  cmpHead: { fontWeight: "700", color: C.ink, marginBottom: 4 }, cmpNow: { fontSize: 18, fontWeight: "800" },
  truth: { color: C.muted, fontSize: 12, marginTop: 8, fontStyle: "italic" },
  metrics: { backgroundColor: C.card, borderRadius: 12, padding: 12, marginTop: 20 },
  feedItem: { borderLeftWidth: 4, paddingLeft: 10, paddingVertical: 6, marginTop: 6 },
  feedTitle: { fontWeight: "800" },
  mRow: { flexDirection: "row", paddingVertical: 4, borderBottomWidth: 1, borderBottomColor: C.line },
  mCell: { flex: 1, fontSize: 12, color: C.ink }, mHead: { color: C.muted, fontWeight: "600" },
  toast: { position: "absolute", top: 12, left: 12, right: 12, zIndex: 10, backgroundColor: "white", borderRadius: 12,
           padding: 12, borderLeftWidth: 6, shadowColor: "#000", shadowOpacity: 0.15, shadowRadius: 12, elevation: 8 },
  toastTitle: { fontWeight: "800", fontSize: 15 }, toastBody: { color: C.ink, marginTop: 2 },
});
