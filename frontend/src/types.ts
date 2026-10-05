export interface Clearance {
  id: string;
  heading_deg: number;
  altitude_ft: number;
  turn: string;
  status: string;
  readback: string;
  acknowledged_at: number | null;
}
export interface Aircraft {
  callsign: string;
  aircraft_type: string;
  x_nm: number;
  y_nm: number;
  altitude_ft: number;
  heading_deg: number;
  track_deg: number;
  speed_kt: number;
  vertical_rate_fpm: number;
  squawk: string;
  control: string;
  human_reason: string | null;
  clearance: Clearance | null;
  stale: boolean;
  age_s: number;
  feed_available: boolean;
  pilot_follows_turn: boolean;
  trajectory: number[][];
  trail: number[][];
}
export interface Alert {
  id: string;
  severity: string;
  kind: string;
  aircraft: string[];
  title: string;
  detail: string;
  evidence: Record<string, number | string>;
  acknowledged: boolean;
}
export interface State {
  version: string;
  session: string;
  time_s: number;
  running: boolean;
  speed: number;
  scenario: string;
  scenario_name: string;
  description: string;
  aircraft: Aircraft[];
  weather: {
    id: string;
    label: string;
    kind: string;
    x_nm: number;
    y_nm: number;
    radius_nm: number;
    floor_ft: number;
    ceiling_ft: number;
  }[];
  weather_age_s: number;
  weather_available: boolean;
  weather_stale: boolean;
  alerts: Alert[];
  events: {
    id: number;
    sim_s: number;
    kind: string;
    callsign: string | null;
    message: string;
  }[];
  system_fault?: string | null;
}
export interface Scenario {
  id: string;
  name: string;
  description: string;
}
export interface Preview {
  status: string;
  unknown: string[];
  findings: Alert[];
  assumptions: string;
}
