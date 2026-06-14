import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface CostData {
  date: string
  cost: number
  input_tokens: number
  output_tokens: number
}

interface Props {
  data: CostData[]
}

export default function CostChart({ data }: Props) {
  if (!data || data.length === 0) {
    return <div className="text-center text-gray-400 py-8">暂无数据</div>
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
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
            return [value.toLocaleString(), name]
          }}
        />
        <Line
          type="monotone"
          dataKey="cost"
          stroke="#f59e0b"
          strokeWidth={2}
          dot={{ fill: '#f59e0b' }}
          name="cost"
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
