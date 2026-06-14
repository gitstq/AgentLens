import { useEffect, useState } from 'react'
import { BarChart3, PieChart, TrendingUp } from 'lucide-react'
import { getAgentTypeStats, getDailyStats, getCostTrends } from '../api/client'
import AgentChart from '../components/AgentChart'
import DailyChart from '../components/DailyChart'
import CostChart from '../components/CostChart'

export default function Analytics() {
  const [agentStats, setAgentStats] = useState([])
  const [dailyStats, setDailyStats] = useState([])
  const [costTrends, setCostTrends] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      getAgentTypeStats(),
      getDailyStats(),
      getCostTrends(),
    ]).then(([agents, daily, costs]) => {
      setAgentStats(agents)
      setDailyStats(daily)
      setCostTrends(costs)
      setLoading(false)
    })
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">分析报表</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <PieChart className="w-5 h-5 text-primary-600" />
            <h3 className="text-lg font-semibold text-gray-900">Agent 类型统计</h3>
          </div>
          <AgentChart data={agentStats.map((a: any) => ({
            agent: a.agent_type,
            sessions: a.sessions,
            tokens: a.total_tokens,
          }))} />
        </div>

        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 className="w-5 h-5 text-primary-600" />
            <h3 className="text-lg font-semibold text-gray-900">每日会话趋势</h3>
          </div>
          <DailyChart data={dailyStats} />
        </div>

        <div className="card lg:col-span-2">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-primary-600" />
            <h3 className="text-lg font-semibold text-gray-900">成本趋势</h3>
          </div>
          <CostChart data={costTrends} />
        </div>
      </div>
    </div>
  )
}
