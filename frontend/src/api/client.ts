import axios from 'axios'
import { Session, AnalyticsSummary } from '../types'

const API_BASE = '/api/v1'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Sessions
export const getSessions = async (): Promise<Session[]> => {
  const { data } = await api.get('/sessions')
  return data
}

export const getSession = async (id: string): Promise<Session> => {
  const { data } = await api.get(`/sessions/${id}`)
  return data
}

export const createSession = async (session: Partial<Session>): Promise<Session> => {
  const { data } = await api.post('/sessions', session)
  return data
}

export const deleteSession = async (id: string): Promise<void> => {
  await api.delete(`/sessions/${id}`)
}

// Commands
export const getCommands = async (sessionId: string) => {
  const { data } = await api.get(`/commands/${sessionId}`)
  return data
}

// Analytics
export const getAnalyticsSummary = async (): Promise<AnalyticsSummary> => {
  const { data } = await api.get('/analytics/summary')
  return data
}

export const getAgentTypeStats = async () => {
  const { data } = await api.get('/analytics/agent-types')
  return data
}

export const getDailyStats = async (days = 30) => {
  const { data } = await api.get('/analytics/daily', { params: { days } })
  return data
}

export const getCostTrends = async (days = 30) => {
  const { data } = await api.get('/analytics/cost-trends', { params: { days } })
  return data
}
