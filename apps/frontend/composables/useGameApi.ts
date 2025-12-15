import { ofetch } from 'ofetch'

export type GameStatus = 'in_progress' | 'win' | 'lose' | 'draw'
export type NextTurn = 'player' | 'computer' | 'none'

export interface MoveResponse {
  board: string[]
  status: GameStatus
  next: NextTurn
  promoCode?: string
}

export const useGameApi = () => {
  const config = useRuntimeConfig()
  const api = ofetch.create({
    baseURL: config.public.apiBase,
    retry: 0
  })

  const makeMove = async (params: {
    board: string[]
    moveIndex: number
    initData?: string | null
    chatId?: string | null
  }): Promise<MoveResponse> => {
    return await api('/api/v1/game/move', {
      method: 'POST',
      body: {
        board: params.board,
        moveIndex: params.moveIndex,
        playerSymbol: 'X',
        initData: params.initData,
        chatId: params.chatId
      }
    })
  }

  const resetGame = async (): Promise<MoveResponse> => {
    return await api('/api/v1/game/reset', { method: 'POST' })
  }

  return { makeMove, resetGame }
}
