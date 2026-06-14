import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Search, Filter, Trash2, Eye } from 'lucide-react'
import { getSessions, deleteSession } from '../api/client'
import { Session } from '../types'

export default function Sessions() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')

  useEffect(() => {
    loadSessions()
  }, [])

  const loadSessions = () => {
    setLoading(true)
    getSessions()
      .then(setSessions)
      .finally(() => setLoading(false))
  }

  const handleDelete = async (id: string) => {
    if (!confirm('确定要删除此会话吗？')) return
    await deleteSession(id)
    loadSessions()
  }

  const filtered = sessions.filter(s =>
    s.agent_type.toLowerCase().includes(filter.toLowerCase()) ||
    (s.project_name?.toLowerCase() || '').includes(filter.toLowerCase())
  )

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">会话列表</h2>
        <div className="relative">
          <Search className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="搜索 Agent 或项目..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 w-64"
          />
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : filtered.length === 0 ? (
        <div className="card text-center py-16">
          <Filter className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">暂无会话数据</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">会话ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Agent</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">项目</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tokens</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">成本</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">时间</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filtered.map((session) => (
                <tr key={session.session_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-mono text-gray-900">{session.session_id}</td>
                  <td className="px-6 py-4">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                      {session.agent_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{session.project_name || '-'}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">{session.total_tokens.toLocaleString()}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">${session.estimated_cost.toFixed(4)}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{session.start_time.slice(0, 16)}</td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => handleDelete(session.session_id)}
                      className="text-red-600 hover:text-red-800 p-1"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
