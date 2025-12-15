import { vi } from 'vitest'

vi.mock('#app', () => ({
  useRuntimeConfig: () => ({ public: { apiBase: 'http://localhost:8000' } })
}))

const navigatorMock = {
  clipboard: {
    writeText: vi.fn().mockResolvedValue(undefined)
  }
}

Object.defineProperty(global, 'navigator', {
  value: navigatorMock,
  writable: true
})
