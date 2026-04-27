import client from './client'
import type { Node, Telemetry, Command, CommandType } from '../types'

export const getNodes = () =>
  client.get<Node[]>('/nodes').then((r) => r.data)

export const getNode = (deviceCode: string) =>
  client.get<Node>(`/nodes/${deviceCode}`).then((r) => r.data)

export const createNode = (data: {
  device_code: string
  name: string
  description?: string
  address?: string
}) => client.post<Node>('/nodes', data).then((r) => r.data)

export const getTelemetry = (deviceCode: string, limit = 100) =>
  client
    .get<Telemetry[]>(`/nodes/${deviceCode}/telemetry`, { params: { limit } })
    .then((r) => r.data)

export const sendCommand = (
  deviceCode: string,
  commandType: CommandType,
  payload?: Record<string, unknown>,
) =>
  client
    .post<Command>(`/nodes/${deviceCode}/commands`, {
      command_type: commandType,
      payload,
    })
    .then((r) => r.data)
