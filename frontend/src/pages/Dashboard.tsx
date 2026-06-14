import { useEffect, useState } from 'react'
import { Activity, Clock, Coins, Command, AlertTriangle, TrendingUp } from 'lucide-react'
import { getAnalyticsSummary } from '../api/client'
import { AnalyticsSummary } from '../types'
import StatCard from '../components/StatCard'
import AgentChart from '../components/AgentChart'
import DailyChart from '../components/DailyChart'

export default function Dashboard() {
  const [data, setData] = useState<AnalyticsSummary | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getAnalyticsSummary()
      .then(setData)
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!data || data.total_sessions === 0) {
    return (
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">仪表盘</h2>
        <div className="card text-center py-16">
          <Activity className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">暂无会话数据</h3>
          <p className="text-gray-500 mb-6">开始使用 AgentLens CLI 记录您的第一个 AI 代理会话</p>
          <code className="bg-gray-100 px-4 py-2 rounded-lg text-sm">
            agentlens start --agent claude
          </code>
        </div>
      </div>
    )
  }

  const hours = Math.floor(data.total_duration_seconds / 3600)
  const minutes = Math.floor((data.total_duration_seconds % 3600) / 60)

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-2xl font-bold text-gray-900">仪表盘</h2>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <TrendingUp className="w-4 h-4" />
          实时数据更新
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          icon={Activity}
          label="总会话数"
          value={data.total_sessions.toString()}
          color="blue"
        />
        <StatCard
          icon={Clock}
          label="总时长"
          value={`${hours}h ${minutes}m`}
          color="green"
        />
        <StatCard
          icon={Coins}
          label="总成本"
          value={`$${data.total_cost.toFixed(4)}`}
          color="yellow"
        />
        <StatCard
          icon={Command}
          label="总命令数"
          value={data.total_commands.toString()}
          color="purple"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <StatCard
          icon={AlertTriangle}
          label="错误数"
          value={data.total_errors.toString()}
          color="red"
        />
        <div className="card">
          <div className="stat-label">平均会话时长</div>
          <div className="stat-value">{data.avg_session_duration.toFixed(0)}s</div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Agent 使用分布</h3>
          <AgentChart data={data.top_agents} />
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">每日趋势</h3>
          <DailyChart data={data.daily_stats} />
        </div>
      </div>
    </div>
  )
}
