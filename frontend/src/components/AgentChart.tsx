import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'

interface AgentData {
  agent: string
  sessions: number
  tokens: number
}

interface Props {
  data: AgentData[]
}

const COLORS = ['#0ea5e9', '#22c55e', '#f59e0b', '#a855f7', '#ef4444', '#6b7280']

export default function AgentChart({ data }: Props) {
  if (!data || data.length === 0) {
    return <div className="text-center text-gray-400 py-8">暂无数据</div>
  }

  const chartData = data.map((item) => ({
    name: item.agent,
    value: item.sessions,
    tokens: item.tokens,
  }))

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
          outerRadius={100}
          fill="#8884d8"
          dataKey="value"
        >
          {chartData.map((_, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          formatter={(value: number, name: string, props: any) => [
            `${value} sessions (${props.payload.tokens} tokens)`,
            name,
          ]}
        />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  )
}
