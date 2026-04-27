import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import { useQuery } from '@tanstack/react-query'
import { getNodes } from '../api/nodes'
import type { Node } from '../types'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

// Fix default marker icon (Leaflet + Vite quirk)
delete (L.Icon.Default.prototype as { _getIconUrl?: unknown })._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const BUENOS_AIRES: [number, number] = [-34.6037, -58.3816]

export default function MapPage() {
  const { data: nodes = [] } = useQuery({ queryKey: ['nodes'], queryFn: getNodes })
  const positioned = nodes.filter((n): n is Node & { latitude: number; longitude: number } =>
    n.latitude !== null && n.longitude !== null,
  )

  return (
    <div className="h-screen w-full">
      <MapContainer
        center={BUENOS_AIRES}
        zoom={13}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {positioned.map((node) => (
          <Marker key={node.id} position={[node.latitude, node.longitude]}>
            <Popup>
              <div className="text-sm">
                <p className="font-semibold">{node.name}</p>
                <p className="text-gray-500">{node.device_code}</p>
                <p className="mt-1">
                  Estado:{' '}
                  <span className={node.is_active ? 'text-green-600' : 'text-red-600'}>
                    {node.is_active ? 'Activo' : 'Inactivo'}
                  </span>
                </p>
                {node.last_seen && (
                  <p className="text-gray-400 text-xs mt-1">
                    Última vez: {new Date(node.last_seen).toLocaleString('es-AR')}
                  </p>
                )}
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  )
}
