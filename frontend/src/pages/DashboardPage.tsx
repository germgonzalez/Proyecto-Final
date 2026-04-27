import { useQuery } from '@tanstack/react-query'
import { getNodes } from '../api/nodes'
import { getAlerts } from '../api/alerts'
import { Activity, Zap, AlertTriangle, CheckCircle } from 'lucide-react'

function StatCard({
  label,
  value,
  icon: Icon,
  color,
}: {
  label: string
  value: number | string
  icon: React.ElementType
  color: string
}) {
  return (
    <div className="bg-white rounded-xl shadow-sm p-5 flex items-center gap-4">
      <div className={`p-3 rounded-lg ${color}`}>
        <Icon size={20} className="text-white" />
      </div>
      <div>
        <p className="text-sm text-gray-500">{label}</p>
        <p className="text-2xl font-bold text-gray-800">{value}</p>
      </div>
    </div>
  )
}

export default function DashboardPage() {
  const { data: nodes = [] } = useQuery({ queryKey: ['nodes'], queryFn: getNodes })
  const { data: alerts = [] } = useQuery({ queryKey: ['alerts'], queryFn: () => getAlerts(false) })

  const active = nodes.filter((n) => n.is_active).length
  const critical = alerts.filter((a) => a.severity === 'critical').length

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-xl font-semibold text-gray-800">Panel General</h2>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Total nodos" value={nodes.length} icon={Zap} color="bg-blue-500" />
        <StatCard label="Activos" value={active} icon={CheckCircle} color="bg-green-500" />
        <StatCard
          label="Alertas activas"
          value={alerts.length}
          icon={AlertTriangle}
          color="bg-yellow-500"
        />
        <StatCard
          label="Críticas"
          value={critical}
          icon={Activity}
          color="bg-red-500"
        />
      </div>

      {/* Tabla de nodos */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b">
          <h3 className="font-medium text-gray-700">Estado de Nodos</h3>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-500 text-xs uppercase">
            <tr>
              <th className="px-5 py-3 text-left">Nombre</th>
              <th className="px-5 py-3 text-left">Código</th>
              <th className="px-5 py-3 text-left">Última conexión</th>
              <th className="px-5 py-3 text-left">Estado</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {nodes.map((node) => (
              <tr key={node.id} className="hover:bg-gray-50">
                <td className="px-5 py-3 font-medium text-gray-800">{node.name}</td>
                <td className="px-5 py-3 text-gray-500 font-mono">{node.device_code}</td>
                <td className="px-5 py-3 text-gray-500">
                  {node.last_seen
                    ? new Date(node.last_seen).toLocaleString('es-AR')
                    : '—'}
                </td>
                <td className="px-5 py-3">
                  <span
                    className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                      node.is_active
                        ? 'bg-green-100 text-green-700'
                        : 'bg-red-100 text-red-700'
                    }`}
                  >
                    {node.is_active ? 'Activo' : 'Inactivo'}
                  </span>
                </td>
              </tr>
            ))}
            {nodes.length === 0 && (
              <tr>
                <td colSpan={4} className="px-5 py-8 text-center text-gray-400">
                  No hay nodos registrados
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
