import { computed, onMounted, ref } from 'vue'

type Impact = 'light' | 'medium' | 'heavy'

type TelegramHaptic = {
  impactOccurred?: (impact: Impact) => void
}

type TelegramWebApp = {
  initDataUnsafe?: { user?: { id?: number; username?: string } }
  initData?: string
  themeParams?: { bg_color?: string }
  ready: () => void
  expand: () => void
  setHeaderColor?: (color: string) => void
  setBackgroundColor?: (color: string) => void
  onEvent: (event: string, cb: () => void) => void
  offEvent?: (event: string, cb: () => void) => void
  HapticFeedback?: TelegramHaptic
}

declare global {
  interface Window {
    Telegram?: { WebApp?: TelegramWebApp }
  }
}

const webAppRef = ref<TelegramWebApp | null>(null)
const themeColorRef = ref('#f5ebe0')
const initDataRef = ref<string | null>(null)
const chatIdRef = ref<string | null>(null)

const parseUserIdFromInitData = (data: string | null): string | null => {
  if (!data) {
    return null
  }
  try {
    const params = new URLSearchParams(data)
    const payload = params.get('user')
    if (!payload) {
      return null
    }
    const parsed = JSON.parse(payload)
    const userId = parsed?.id
    return typeof userId === 'number' ? String(userId) : null
  } catch {
    return null
  }
}

const parseInitDataFromLocation = (): string | null => {
  if (typeof window === 'undefined') {
    return null
  }

  const extract = (query: string): string | null => {
    if (!query) return null
    const params = new URLSearchParams(query)
    const encoded = params.get('tgWebAppData')
    return encoded ? decodeURIComponent(encoded) : null
  }

  const fromHash = extract(window.location.hash.startsWith('#') ? window.location.hash.slice(1) : window.location.hash)
  if (fromHash) return fromHash

  return extract(window.location.search.startsWith('?') ? window.location.search.slice(1) : window.location.search)
}

const loadStored = () => {
  if (typeof window === 'undefined') return { initData: null as string | null, chatId: null as string | null }
  return {
    initData: sessionStorage.getItem('tg_init_data'),
    chatId: sessionStorage.getItem('tg_chat_id')
  }
}

const parseChatIdFromUrl = (): string | null => {
  if (typeof window === 'undefined') return null
  const params = new URLSearchParams(window.location.search.startsWith('?') ? window.location.search.slice(1) : window.location.search)
  const chatId = params.get('chat_id') || params.get('chatId')
  return chatId && chatId.trim() ? chatId.trim() : null
}

const persistStored = (initData: string | null, chatId: string | null) => {
  if (typeof window === 'undefined') return
  if (initData) {
    sessionStorage.setItem('tg_init_data', initData)
  }
  if (chatId) {
    sessionStorage.setItem('tg_chat_id', chatId)
  }
}

export function useTelegramWebApp() {
  onMounted(() => {
    if (typeof window === 'undefined') {
      return
    }
    const stored = loadStored()
    const tg = window.Telegram?.WebApp
    const fallbackInitData = parseInitDataFromLocation()
    const urlChatId = parseChatIdFromUrl()

    if (!tg) {
      initDataRef.value = fallbackInitData || stored.initData
      chatIdRef.value = urlChatId || parseUserIdFromInitData(initDataRef.value) || stored.chatId
      persistStored(initDataRef.value, chatIdRef.value)
      return
    }

    webAppRef.value = tg
    const resolvedInitData = tg.initData || fallbackInitData || stored.initData
    initDataRef.value = resolvedInitData
    chatIdRef.value =
      urlChatId ||
      (tg.initDataUnsafe?.user?.id ? String(tg.initDataUnsafe.user.id) : null) ||
      parseUserIdFromInitData(resolvedInitData) ||
      stored.chatId
    persistStored(initDataRef.value, chatIdRef.value)

    themeColorRef.value = tg.themeParams?.bg_color || '#f5ebe0'
    tg.setBackgroundColor?.('#f5ebe0')
    tg.ready()
    tg.expand()
    tg.onEvent('themeChanged', () => {
      themeColorRef.value = tg.themeParams?.bg_color || '#f5ebe0'
    })
  })

  const triggerHaptic = (impact: Impact = 'light') => {
    webAppRef.value?.HapticFeedback?.impactOccurred?.(impact)
  }

  return {
    webApp: computed(() => webAppRef.value),
    initData: computed(() => initDataRef.value),
    themeColor: computed(() => themeColorRef.value),
    chatId: computed(() => chatIdRef.value),
    triggerHaptic
  }
}
