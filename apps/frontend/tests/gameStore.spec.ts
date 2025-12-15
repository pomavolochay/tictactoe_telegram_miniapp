import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const makeMoveMock = vi.fn()
const resetGameMock = vi.fn()
const hapticMock = vi.fn()

vi.mock('~/composables/useGameApi', () => ({
  useGameApi: () => ({
    makeMove: makeMoveMock,
    resetGame: resetGameMock
  })
}))

vi.mock('~/composables/useTelegramWebApp', () => ({
  useTelegramWebApp: () => ({
    initData: { value: 'init' },
    triggerHaptic: hapticMock
  })
}))

import { useGameStore } from '../stores/game'

describe('useGameStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    makeMoveMock.mockReset()
    resetGameMock.mockReset()
    hapticMock.mockReset()
  })

  it('updates board and promo on win', async () => {
    makeMoveMock.mockResolvedValue({
      board: ['X', '', '', '', '', '', '', '', ''],
      status: 'win',
      next: 'none',
      promoCode: 'PRIZE'
    })
    const store = useGameStore()
    await store.playerMove(0)
    expect(store.board[0]).toBe('X')
    expect(store.status).toBe('win')
    expect(store.promoCode).toBe('PRIZE')
    expect(hapticMock).toHaveBeenCalledWith('medium')
  })

  it('resets board from api', async () => {
    resetGameMock.mockResolvedValue({
      board: Array(9).fill(''),
      status: 'in_progress',
      next: 'player'
    })
    const store = useGameStore()
    await store.resetGame()
    expect(store.status).toBe('in_progress')
    expect(store.next).toBe('player')
    expect(store.isReady).toBe(true)
  })

  it('captures errors from api', async () => {
    makeMoveMock.mockRejectedValue(new Error('boom'))
    const store = useGameStore()
    await store.playerMove(0)
    expect(store.error).toBe('boom')
  })
})
