import client from './client'
import type { Alert } from '../types'

export const getAlerts = (includeResolved = false) =>
  client
    .get<Alert[]>('/alerts', { params: { include_resolved: includeResolved } })
    .then((r) => r.data)

export const resolveAlert = (alertId: number) =>
  client.patch<Alert>(`/alerts/${alertId}/resolve`).then((r) => r.data)
