export interface Node {
  id: number
  device_code: string
  name: string
  description: string | null
  address: string | null
  latitude: number | null
  longitude: number | null
  is_active: boolean
  installed_at: string | null
  last_seen: string | null
  created_at: string
}

export interface Telemetry {
  id: number
  node_id: number
  timestamp: string
  received_at: string
  voltage: number | null
  current: number | null
  power: number | null
  power_factor: number | null
  dimming_level: number | null
  is_on: boolean | null
  status_ok: boolean | null
  latitude: number | null
  longitude: number | null
}

export type CommandType = 'set_dimming' | 'turn_on' | 'turn_off'
export type CommandStatus = 'pending' | 'executed' | 'failed'

export interface Command {
  id: number
  node_id: number
  command_type: CommandType
  payload: Record<string, unknown> | null
  status: CommandStatus
  created_by: string | null
  created_at: string
  executed_at: string | null
  acknowledged_at: string | null
}

export type AlertType =
  | 'offline'
  | 'voltage_high'
  | 'voltage_low'
  | 'power_high'
  | 'power_factor_low'
  | 'lamp_failure'
  | 'communication_error'

export type AlertSeverity = 'info' | 'warning' | 'critical'

export interface Alert {
  id: number
  node_id: number
  alert_type: AlertType
  severity: AlertSeverity
  message: string
  is_resolved: boolean
  created_at: string
  resolved_at: string | null
}
