import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getNodes, sendCommand, createNode } from '../api/nodes'
import { Plus, Zap, Power, PowerOff } from 'lucide-react'
import type { Node } from '../types'

function DimmingControl({ node }: { node: Node }) {
  const [dimming, setDimming] = useState(100)
  const qc = useQueryClient()
  const { mutate: send, isPending } = useMutation({
    mutationFn: (type: 'set_dimming' | 'turn_on' | 'turn_off') =>
      sendCommand(node.device_code, type, type === 'set_dimming' ? { dimming } : undefined),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['nodes'] }),
  })

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <input
          type="range"
          min={0}
          max={100}
          value={dimming}
          onChange={(e) => setDimming(Number(e.target.value))}
          className="flex-1 accent-blue-600"
        />
        <span className="text-sm font-mono w-10 text-right">{dimming}%</span>
        <button
          onClick={() => send('set_dimming')}
          disabled={isPending}
          className="flex items-center gap-1 px-3 py-1.5 bg-blue-600 text-white text-xs rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          <Zap size={12} />
          Aplicar
        </button>
      </div>
      <div className="flex gap-2">
        <button
          onClick={() => send('turn_on')}
          disabled={isPending}
          className="flex items-center gap-1 px-3 py-1.5 bg-green-600 text-white text-xs rounded-lg hover:bg-green-700 disabled:opacity-50"
        >
          <Power size={12} />
          Encender
        </button>
        <button
          onClick={() => send('turn_off')}
          disabled={isPending}
          className="flex items-center gap-1 px-3 py-1.5 bg-gray-600 text-white text-xs rounded-lg hover:bg-gray-700 disabled:opacity-50"
        >
          <PowerOff size={12} />
          Apagar
        </button>
      </div>
    </div>
  )
}

function AddNodeModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient()
  const [form, setForm] = useState({ device_code: '', name: '', address: '' })
  const { mutate, isPending, error } = useMutation({
    mutationFn: createNode,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['nodes'] }); onClose() },
  })

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-md space-y-4">
        <h3 className="text-lg font-semibold">Registrar nuevo nodo</h3>
        {['device_code', 'name', 'address'].map((field) => (
          <div key={field}>
            <label className="block text-sm text-gray-600 mb-1 capitalize">
              {field.replace('_', ' ')}
            </label>
            <input
              className="w-full border rounded-lg px-3 py-2 text-sm"
              value={form[field as keyof typeof form]}
              onChange={(e) => setForm((f) => ({ ...f, [field]: e.target.value }))}
            />
          </div>
        ))}
        {error && <p className="text-red-600 text-sm">Error al registrar el nodo</p>}
        <div className="flex justify-end gap-2">
          <button onClick={onClose} className="px-4 py-2 text-sm text-gray-600 hover:underline">
            Cancelar
          </button>
          <button
            onClick={() => mutate(form)}
            disabled={isPending || !form.device_code || !form.name}
            className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {isPending ? 'Guardando...' : 'Guardar'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default function NodesPage() {
  const { data: nodes = [] } = useQuery({ queryKey: ['nodes'], queryFn: getNodes })
  const [showAdd, setShowAdd] = useState(false)

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-800">Gestión de Nodos</h2>
        <button
          onClick={() => setShowAdd(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700"
        >
          <Plus size={16} />
          Nuevo nodo
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {nodes.map((node) => (
          <div key={node.id} className="bg-white rounded-xl shadow-sm p-5 space-y-4">
            <div className="flex items-start justify-between">
              <div>
                <p className="font-semibold text-gray-800">{node.name}</p>
                <p className="text-xs text-gray-400 font-mono">{node.device_code}</p>
                {node.address && <p className="text-xs text-gray-500 mt-0.5">{node.address}</p>}
              </div>
              <span
                className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${
                  node.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                }`}
              >
                {node.is_active ? 'Activo' : 'Inactivo'}
              </span>
            </div>
            <DimmingControl node={node} />
          </div>
        ))}
        {nodes.length === 0 && (
          <p className="text-gray-400 col-span-3 text-center py-10">No hay nodos registrados</p>
        )}
      </div>

      {showAdd && <AddNodeModal onClose={() => setShowAdd(false)} />}
    </div>
  )
}
