import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getAlerts, resolveAlert } from '../api/alerts'
import { CheckCircle, AlertTriangle, AlertCircle, Info } from 'lucide-react'
import type { AlertSeverity } from '../types'

const severityConfig: Record<AlertSeverity, { label: string; icon: React.ElementType; classes: string }> = {
  critical: { label: 'Crítica', icon: AlertCircle, classes: 'bg-red-50 text-red-700 border-red-200' },
  warning: { label: 'Advertencia', icon: AlertTriangle, classes: 'bg-yellow-50 text-yellow-700 border-yellow-200' },
  info: { label: 'Info', icon: Info, classes: 'bg-blue-50 text-blue-700 border-blue-200' },
}

export default function AlertsPage() {
  const qc = useQueryClient()
  const { data: alerts = [], isLoading } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => getAlerts(false),
  })

  const { mutate: resolve } = useMutation({
    mutationFn: resolveAlert,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['alerts'] }),
  })

  return (
    <div className="p-6 space-y-4">
      <h2 className="text-xl font-semibold text-gray-800">Alertas Activas</h2>

      {isLoading && <p className="text-gray-400">Cargando...</p>}

      {alerts.length === 0 && !isLoading && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-8 text-center">
          <CheckCircle className="mx-auto text-green-500 mb-2" size={32} />
          <p className="text-green-700 font-medium">Sin alertas activas</p>
        </div>
      )}

      <div className="space-y-3">
        {alerts.map((alert) => {
          const cfg = severityConfig[alert.severity]
          const Icon = cfg.icon
          return (
            <div
              key={alert.id}
              className={`border rounded-xl p-4 flex items-start justify-between gap-4 ${cfg.classes}`}
            >
              <div className="flex items-start gap-3">
                <Icon size={18} className="mt-0.5 shrink-0" />
                <div>
                  <p className="font-medium text-sm">{alert.message}</p>
                  <p className="text-xs opacity-70 mt-0.5">
                    {cfg.label} · Nodo #{alert.node_id} ·{' '}
                    {new Date(alert.created_at).toLocaleString('es-AR')}
                  </p>
                </div>
              </div>
              <button
                onClick={() => resolve(alert.id)}
                className="shrink-0 text-xs font-medium underline opacity-70 hover:opacity-100"
              >
                Resolver
              </button>
            </div>
          )
        })}
      </div>
    </div>
  )
}
