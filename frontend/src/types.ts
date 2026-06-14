export interface Session {
  id: number
  session_id: string
  agent_type: string
  agent_version?: string
  project_name?: string
  start_time: string
  end_time?: string
  duration_seconds: number
  input_tokens: number
  output_tokens: number
  total_tokens: number
  estimated_cost: number
  command_count: number
  file_changes: number
  error_count: number
  tags?: string
  created_at: string
}

export interface CommandLog {
  id: number
  session_id: string
  command: string
  response?: string
  timestamp: string
  duration_ms: number
  tokens_used: number
  command_type?: string
}

export interface AnalyticsSummary {
  total_sessions: number
  total_duration_seconds: number
  total_tokens: number
  total_cost: number
  total_commands: number
  total_errors: number
  avg_session_duration: number
  avg_tokens_per_session: number
  top_agents: Array<{
    agent: string
    sessions: number
    tokens: number
  }>
  daily_stats: Array<{
    date: string
    sessions: number
    tokens: number
    cost: number
  }>
}
