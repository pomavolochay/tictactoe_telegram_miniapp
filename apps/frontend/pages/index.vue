<template>
  <main class="relative flex min-h-screen items-center justify-center overflow-hidden px-4 py-10">
    <div class="pointer-events-none absolute inset-0">
      <div class="absolute inset-y-10 left-0 h-64 w-64 -translate-x-1/3 rounded-full bg-petal blur-3xl" />
      <div class="absolute bottom-0 right-4 h-64 w-64 translate-y-1/3 rounded-full bg-mist blur-3xl" />
    </div>

    <div class="relative z-10 grid w-full max-w-4xl gap-8 rounded-[32px] border border-white/50 bg-white/70 p-6 shadow-2xl backdrop-blur-lg md:grid-cols-[1.1fr,0.9fr]">
      <section class="flex flex-col justify-between gap-6">
        <div>
          <p class="text-xs uppercase tracking-[0.6em] text-plum/70">{{ heroBadge }}</p>
          <h1 class="mt-3 font-serif text-4xl text-cocoa md:text-5xl">
            {{ heroTitle }}
          </h1>
          <p class="mt-3 text-base text-cocoa/70">
            {{ heroDescription }}
          </p>
        </div>
        <div class="rounded-full bg-mist/80 px-4 py-2 text-sm text-sage shadow-inner">
          {{ hintChipLabel }}:
          <span class="font-semibold text-cocoa">{{ statusHint }}</span>
        </div>
        <div class="rounded-2xl border border-lilac/30 bg-white/70 p-4 text-sm text-cocoa/70 shadow-inner">
          <p v-for="line in instructionLines" :key="line">{{ line }}</p>
        </div>
      </section>

      <section class="flex flex-col gap-5">
        <div class="rounded-[28px] border border-lilac/40 bg-white/80 p-5 shadow-xl">
          <Board :cells="store.board" :disabled="boardDisabled" @select="onSelect" />
          <p class="mt-4 text-center text-sm text-cocoa/60">
            {{ boardCaption }}
          </p>
        </div>

        <p v-if="store.error" class="rounded-2xl bg-coral/20 px-4 py-3 text-center text-sm text-plum">{{ store.error }}</p>

        <div class="flex flex-wrap items-center justify-between gap-4 text-sm text-cocoa/70">
          <span>
            {{ turnLabel }}:
            <strong class="text-cocoa">{{ currentTurn }}</strong>
          </span>

          <div class="flex gap-2">
            <button
              class="rounded-full bg-mist px-5 py-2 text-sm font-semibold text-cocoa shadow-sm transition hover:bg-mist/70 disabled:opacity-60"
              type="button"
              :disabled="store.isLoading"
              @click="store.resetGame"
            >
              {{ refreshButtonLabel }}
            </button>
            <button
              class="rounded-full border border-plum/20 bg-plum/90 px-5 py-2 text-sm font-semibold text-white shadow-lg transition hover:-translate-y-0.5 disabled:opacity-60"
              type="button"
              :disabled="store.isLoading || !store.isBoardLocked"
              @click="store.resetGame"
            >
              {{ playAgainButtonLabel }}
            </button>
          </div>
        </div>
      </section>
    </div>

    <ResultModal
      :visible="store.hasResult"
      :status="store.status"
      :title="store.resultTitle"
      :description="store.resultDescription"
      :promo-code="store.promoCode"
      @reset="store.resetGame"
      @copy="copyPromo"
    />

    <transition name="fade">
      <div
        v-if="copied"
        class="fixed bottom-6 left-1/2 -translate-x-1/2 rounded-full bg-plum px-6 py-2 text-sm text-white shadow-xl"
      >
        {{ toastText }}
      </div>
    </transition>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import Board from '~/components/Board.vue'
import ResultModal from '~/components/ResultModal.vue'
import { useGameStore } from '~/stores/game'

const store = useGameStore()
const copied = ref(false)

const heroBadge = '\u0423\u044e\u0442\u043d\u044b\u0439 \u0447\u0435\u043b\u043b\u0435\u043d\u0434\u0436'
const heroTitle = '\u0422\u0432\u043e\u044f \u0443\u044e\u0442\u043d\u0430\u044f TicTacToe-\u0432\u0441\u0435\u043b\u0435\u043d\u043d\u0430\u044f'
const heroDescription =
  '\u0421\u044b\u0433\u0440\u0430\u0439 \u043f\u0440\u043e\u0442\u0438\u0432 \u0434\u0440\u0443\u0436\u0435\u043b\u044e\u0431\u043d\u043e\u0433\u043e AI: \u043e\u043d \u043b\u044e\u0431\u0438\u0442 \u0432\u044b\u0441\u0447\u0438\u0442\u0430\u043d\u043d\u044b\u0435 \u0445\u043e\u0434\u044b, \u043d\u043e \u043d\u0435 \u0441\u043f\u043e\u0441\u043e\u0431\u0435\u043d \u0441\u043f\u0440\u044f\u0442\u0430\u0442\u044c\u0441\u044f \u043e\u0442 \u0442\u0432\u043e\u0435\u0439 \u0438\u043d\u0442\u0443\u0438\u0446\u0438\u0438.'
const hintChipLabel = '\u041f\u043e\u0434\u0441\u043a\u0430\u0437\u043a\u0430'
const instructionLines = [
  '\u0058 \u2014 \u0442\u0432\u043e\u0439 \u0441\u0438\u043c\u0432\u043e\u043b, \u043f\u043e\u043b\u043d\u044b\u0439 \u0443\u0432\u0435\u0440\u0435\u043d\u043d\u043e\u0441\u0442\u0438',
  '\u004f \u2014 \u0440\u0435\u0448\u0438\u043c\u043e\u0441\u0442\u044c \u043a\u043e\u043c\u043f\u044c\u044e\u0442\u0435\u0440\u0430',
  '\u041f\u0443\u0441\u0442\u0430\u044f \u043a\u043b\u0435\u0442\u043a\u0430 \u2014 \u043c\u0435\u0441\u0442\u043e \u0434\u043b\u044f \u043d\u043e\u0432\u043e\u0433\u043e \u043c\u0438\u043a\u0440\u043e-\u043f\u043e\u0434\u0432\u0438\u0433\u0430',
]
const turnLabel = '\u0427\u0435\u0439 \u0445\u043e\u0434'
const playerTurnLabel = '\u0422\u044b'
const computerTurnLabel = '\u041a\u043e\u043c\u043f\u044c\u044e\u0442\u0435\u0440'
const aiThinkingLabel = '\u0418\u0418 \u0434\u0443\u043c\u0430\u0435\u0442...'
const noTurnLabel = '\u041f\u0430\u0440\u0442\u0438\u044f \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u0430'
const refreshButtonLabel = '\u041e\u0431\u043d\u043e\u0432\u0438\u0442\u044c \u043f\u043e\u043b\u0435'
const playAgainButtonLabel = '\u0421\u044b\u0433\u0440\u0430\u0442\u044c \u0435\u0449\u0451 \u0440\u0430\u0437'
const toastText = '\u041f\u0440\u043e\u043c\u043e\u043a\u043e\u0434 \u0441\u043a\u043e\u043f\u0438\u0440\u043e\u0432\u0430\u043d!'

const boardDisabled = computed(() => store.isBoardLocked || store.isLoading)

const statusHint = computed(() => {
  if (store.status === 'win') return '\u0417\u0430\u0431\u0435\u0440\u0438 \u043f\u0440\u043e\u043c\u043e\u043a\u043e\u0434'
  if (store.status === 'lose') return '\u041f\u043e\u043f\u0440\u043e\u0431\u0443\u0439 \u043d\u043e\u0432\u0443\u044e \u0442\u0430\u043a\u0442\u0438\u043a\u0443'
  if (store.status === 'draw') return '\u0427\u0435\u0441\u0442\u043d\u0430\u044f \u043d\u0438\u0447\u044c\u044f'
  return '\u0421\u043b\u0435\u0434\u0438 \u0437\u0430 \u0448\u0430\u0433\u0430\u043c\u0438 AI'
})

const boardCaption = computed(() => {
  if (store.status === 'win') return '\u041f\u043e\u043b\u0435 \u0436\u0434\u0451\u0442 \u043d\u043e\u0432\u0443\u044e \u0441\u0442\u0440\u0430\u0442\u0435\u0433\u0438\u044e, \u043a\u043e\u0442\u043e\u0440\u0430\u044f \u0442\u0430\u043a \u0436\u0435 \u043c\u044f\u0433\u043a\u0430.'
  if (store.status === 'lose') return '\u0420\u0435\u0432\u0430\u043d\u0448 \u0443\u0436\u0435 \u0440\u044f\u0434\u043e\u043c: \u043a\u043e\u043c\u043f\u044c\u044e\u0442\u0435\u0440 \u0432\u0441\u0435\u0433\u043e \u043b\u0438\u0448\u044c \u043d\u0435\u0441\u043a\u043e\u043b\u044c\u043a\u043e \u0445\u043e\u0434\u043e\u0432 \u0432\u043f\u0435\u0440\u0451\u0434.'
  if (store.status === 'draw') return '\u0421\u0438\u043b\u044b \u0440\u0430\u0432\u043d\u044b \u2014 \u043d\u0430\u0436\u043c\u0438 \u0441\u0431\u0440\u043e\u0441 \u0438 \u0437\u0430\u0434\u0430\u0439 \u043d\u043e\u0432\u0443\u044e \u043b\u0435\u043a\u0433\u0443\u044e \u0441\u0442\u0440\u0430\u0442\u0435\u0433\u0438\u044e.'
  return '\u0412\u044b\u0431\u0435\u0440\u0438 \u043a\u043b\u0435\u0442\u043a\u0443, \u0447\u0442\u043e\u0431\u044b \u0441\u0434\u0435\u043b\u0430\u0442\u044c \u043c\u044f\u0433\u043a\u0438\u0439 \u043f\u0435\u0440\u0432\u044b\u0439 \u0445\u043e\u0434.'
})

const currentTurn = computed(() => {
  if (store.hasResult) return noTurnLabel
  if (store.isLoading) return aiThinkingLabel
  if (store.next === 'player') return playerTurnLabel
  if (store.next === 'computer') return computerTurnLabel
  return noTurnLabel
})

const onSelect = (index: number) => {
  if (boardDisabled.value) return
  store.playerMove(index)
}

const copyPromo = async () => {
  if (!store.promoCode) return
  try {
    await navigator.clipboard.writeText(store.promoCode)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 1500)
  } catch {
    // ignore
  }
}

onMounted(() => {
  store.bootstrap()
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
