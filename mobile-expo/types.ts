export type Level = "SAFE" | "WATCH" | "DANGER";
export type Alert = { kind: "watch" | "danger" | "sensor" | "resolved"; title: string; body: string; severity: 0 | 1 | 2 };
export type Point = {
  time: string; do: number | null; do_smooth: number | null; ph: number | null; temp: number | null;
  anomaly: number; reliability: number; risk: number; level: Level;
  sensor_check: boolean; other_sensor_issue: boolean; threshold_alert: boolean;
  event: string; reasons: string[]; action: string;
  flags: { watch: boolean; danger: boolean; sensor_check: boolean };  // current state (every point)
  alert: Alert | null;                                                // only when a notification should fire
};
export type Summary = { threshold_first_alarm: number | null; pondguard_first_danger: number | null; pondguard_first_sensor_check: number | null };
export type SimResult = { pond: string; event: string | null; start_index: number | null; step_minutes: number; points: Point[]; summary: Summary };
export type Scenario = { title: string; narrative: string; events: { type: string; start_hour: number; intensity: number }[] };
export type PondInfo = { pond: string; points: number; hours: number; showcase: boolean };
export type EventInfo = { id: string; label: string; kind: "risk" | "sensor" };
export type MetricRow = { method: string; precision: number; recall: number; f1: number;
  false_alarms_per_day: number; sensor_faults_raised_as_danger: string; event_recall: string; median_delay_min: number | null };
export type DemoBundle = { ponds: PondInfo[]; events: EventInfo[]; metrics: MetricRow[]; drift: any[];
  scenarios: Record<string, SimResult & { scenario?: Scenario; source?: string }> };

/** Messages from the WebSocket /ws/run */
export type WsMsg =
  | { type: "status"; text: string }
  | { type: "scenario"; scenario: Scenario; source: string; pond: string; start_index: number | null; step_minutes: number; total: number }
  | { type: "history"; points: Point[] }
  | { type: "point"; i: number; point: Point }
  | { type: "end"; summary: Summary }
  | { type: "error"; detail: string };
