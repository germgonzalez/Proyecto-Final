import { Routes, Route, NavLink } from 'react-router-dom'
import { MapPin, LayoutDashboard, Bell, Settings } from 'lucide-react'
import clsx from 'clsx'
import MapPage from './pages/MapPage'
import DashboardPage from './pages/DashboardPage'
import AlertsPage from './pages/AlertsPage'
import NodesPage from './pages/NodesPage'

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/map', label: 'Mapa', icon: MapPin },
  { to: '/alerts', label: 'Alertas', icon: Bell },
  { to: '/nodes', label: 'Nodos', icon: Settings },
]

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-56 bg-gray-900 text-white flex flex-col">
        <div className="px-6 py-5 border-b border-gray-700">
          <h1 className="text-sm font-semibold text-gray-300 uppercase tracking-widest">
            Telegestión
          </h1>
          <p className="text-xs text-gray-500 mt-0.5">Luminarias LED</p>
        </div>
        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:bg-gray-800 hover:text-white',
                )
              }
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/map" element={<MapPage />} />
          <Route path="/alerts" element={<AlertsPage />} />
          <Route path="/nodes" element={<NodesPage />} />
        </Routes>
      </main>
    </div>
  )
}
