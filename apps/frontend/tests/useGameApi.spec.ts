import { beforeEach, describe, expect, it, vi } from 'vitest'

const fetchMock = vi.fn()
vi.mock('ofetch', () => ({
  ofetch: { create: () => fetchMock }
}))

import { useGameApi } from '../composables/useGameApi'

describe('useGameApi', () => {
  beforeEach(() => {
    fetchMock.mockReset()
  })

  it('sends move payload to backend', async () => {
    fetchMock.mockResolvedValue({ board: [], status: 'in_progress', next: 'computer' })
    const api = useGameApi()
    const body = { board: Array(9).fill(''), moveIndex: 4, initData: 'data' }
    const response = await api.makeMove(body)
    expect(fetchMock).toHaveBeenCalledWith('/api/v1/game/move', expect.objectContaining({ method: 'POST' }))
    expect(response.status).toBe('in_progress')
  })

  it('calls reset endpoint', async () => {
    fetchMock.mockResolvedValue({ board: Array(9).fill(''), status: 'in_progress', next: 'player' })
    const api = useGameApi()
    const result = await api.resetGame()
    expect(fetchMock).toHaveBeenCalledWith('/api/v1/game/reset', expect.objectContaining({ method: 'POST' }))
    expect(result.next).toBe('player')
  })
})
