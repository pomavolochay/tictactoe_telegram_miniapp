import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { useGameApi, type GameStatus, type NextTurn } from '~/composables/useGameApi'
import { useTelegramWebApp } from '~/composables/useTelegramWebApp'

const unexpectedError = '\u041d\u0435\u043f\u0440\u0435\u0434\u0432\u0438\u0434\u0435\u043d\u043d\u0430\u044f \u043e\u0448\u0438\u0431\u043a\u0430'

const emptyBoard = (): string[] => Array(9).fill('')

const toErrorMessage = (err: unknown): string => {
  if (err instanceof Error && err.message) {
    return err.message
  }
  return unexpectedError
}

export const useGameStore = defineStore('game', () => {
  const api = useGameApi()
  const telegram = useTelegramWebApp()

  const board = ref<string[]>(emptyBoard())
  const status = ref<GameStatus>('in_progress')
  const next = ref<NextTurn>('player')
  const promoCode = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const isReady = ref(false)

  const isBoardLocked = computed(() => status.value !== 'in_progress')
  const hasResult = computed(() => status.value !== 'in_progress')

  const resultTitle = computed(() => {
    if (status.value === 'win') return '\u0423\u0440\u0430!\u0020\u0422\u044b\u0020\u043f\u043e\u0431\u0435\u0434\u0438\u043b\u0430'
    if (status.value === 'lose') return '\u0417\u0430\u0431\u0435\u0440\u0451\u043c\u0020\u0440\u0435\u0432\u0430\u043d\u0448?'
    if (status.value === 'draw') return '\u041d\u0438\u0447\u044c\u044f'
    return ''
  })

  const resultDescription = computed(() => {
    if (status.value === 'win') {
      return '\u0417\u0430\u0431\u0435\u0440\u0438\u0020\u0441\u0432\u043e\u0439\u0020\u043f\u0440\u043e\u043c\u043e\u043a\u043e\u0434\u0020\u0438\u0020\u0434\u043e\u0431\u0430\u0432\u044c\u0020\u043d\u0435\u043c\u043d\u043e\u0433\u043e\u0020\u0440\u043e\u0441\u043a\u043e\u0448\u0438\u0020\u0432\u0020\u0434\u0435\u043d\u044c.'
    }
    if (status.value === 'lose') {
      return '\u041d\u0435\u0020\u043f\u0435\u0440\u0435\u0436\u0438\u0432\u0430\u0439:\u0020\u043f\u0430\u0440\u0430\u0020\u0448\u0430\u0433\u043e\u0432\u0020\u0432\u0020\u043d\u043e\u0432\u043e\u043c\u0020\u0442\u0435\u043c\u043f\u0435\u0020\u2014\u0020\u0438\u0020\u043f\u043e\u0431\u0435\u0434\u0430\u0020\u0431\u0443\u0434\u0435\u0442\u0020\u043d\u0430\u0020\u0442\u0432\u043e\u0435\u0439\u0020\u0441\u0442\u043e\u0440\u043e\u043d\u0435.'
    }
    if (status.value === 'draw') {
      return '\u0412\u0441\u0451\u0020\u0447\u0435\u0441\u0442\u043d\u043e:\u0020\u043e\u0431\u043d\u043e\u0432\u0438\u0020\u043f\u043e\u043b\u0435\u0020\u0438\u0020\u043f\u043e\u043f\u0440\u043e\u0431\u0443\u0439\u0020\u0441\u0020\u043d\u043e\u0432\u043e\u0439\u0020\u0442\u0430\u043a\u0442\u0438\u043a\u043e\u0439.'
    }
    return ''
  })

  const updateFromResponse = (payload: { board: string[]; status: GameStatus; next: NextTurn; promoCode?: string | null }) => {
    board.value = [...payload.board]
    status.value = payload.status
    next.value = payload.next
    promoCode.value = payload.promoCode ?? null
  }

  const playerMove = async (index: number) => {
    if (isLoading.value || isBoardLocked.value || board.value[index]) {
      return
    }
    isLoading.value = true
    error.value = null
    try {
      const response = await api.makeMove({
        board: board.value,
        moveIndex: index,
        initData: telegram.initData.value ?? undefined,
        chatId: telegram.chatId.value ?? undefined,
      })
      updateFromResponse(response)
      telegram.triggerHaptic(response.status === 'win' ? 'medium' : 'light')
    } catch (err) {
      error.value = toErrorMessage(err)
    } finally {
      isLoading.value = false
    }
  }

  const resetGame = async () => {
    if (isLoading.value) return
    isLoading.value = true
    error.value = null
    try {
      const response = await api.resetGame()
      updateFromResponse(response)
      promoCode.value = null
    } catch (err) {
      board.value = emptyBoard()
      status.value = 'in_progress'
      next.value = 'player'
      promoCode.value = null
      error.value = toErrorMessage(err)
    } finally {
      isLoading.value = false
      isReady.value = true
    }
  }

  const bootstrap = async () => {
    if (isReady.value) return
    await resetGame()
  }

  return {
    board,
    status,
    next,
    promoCode,
    isLoading,
    error,
    isReady,
    isBoardLocked,
    hasResult,
    resultTitle,
    resultDescription,
    playerMove,
    resetGame,
    bootstrap,
  }
})
