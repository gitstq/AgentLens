import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface DailyData {
  date: string
  sessions: number
  tokens: number
  cost: number
}

interface Props {
  data: DailyData[]
}

export default function DailyChart({ data }: Props) {
  if (!data || data.length === 0) {
    return <div className="text-center text-gray-400 py-8">暂无数据</div>
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="date"
          tickFormatter={(value) => value.slice(5)}
          fontSize={12}
        />
        <YAxis fontSize={12} />
        <Tooltip
          formatter={(value: number, name: string) => {
            if (name === 'cost') return [`$${value.toFixed(4)}`, '成本']
            if (name === 'tokens') return [value.toLocaleString(), 'Tokens']
            return [value, '会话数']
          }}
        />
        <Bar dataKey="sessions" fill="#0ea5e9" name="sessions" />
        <Bar dataKey="tokens" fill="#22c55e" name="tokens" />
      </BarChart>
    </ResponsiveContainer>
  )
}
