import { LucideIcon } from 'lucide-react'

interface StatCardProps {
  icon: LucideIcon
  label: string
  value: string
  color: 'blue' | 'green' | 'yellow' | 'purple' | 'red'
}

const colorMap = {
  blue: 'bg-blue-50 text-blue-600',
  green: 'bg-green-50 text-green-600',
  yellow: 'bg-yellow-50 text-yellow-600',
  purple: 'bg-purple-50 text-purple-600',
  red: 'bg-red-50 text-red-600',
}

export default function StatCard({ icon: Icon, label, value, color }: StatCardProps) {
  return (
    <div className="card">
      <div className="flex items-center gap-4">
        <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${colorMap[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
        <div>
          <div className="stat-label">{label}</div>
          <div className="stat-value">{value}</div>
        </div>
      </div>
    </div>
  )
}
