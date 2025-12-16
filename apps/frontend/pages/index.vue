<template>
  <main class="relative flex min-h-screen items-center justify-center overflow-hidden px-4 py-10" :aria-busy="store.isLoading">
    <div class="pointer-events-none absolute inset-0">
      <div class="absolute inset-y-10 left-0 h-64 w-64 -translate-x-1/3 rounded-full bg-petal blur-3xl" />
      <div class="absolute bottom-0 right-4 h-64 w-64 translate-y-1/3 rounded-full bg-mist blur-3xl" />
    </div>

    <div
      class="relative z-10 grid w-full max-w-4xl gap-8 rounded-[32px] border border-white/50 bg-white/70 p-6 shadow-2xl backdrop-blur-lg md:grid-cols-[1.1fr,0.9fr]"
    >
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

        <p v-if="store.error" class="rounded-2xl bg-coral/20 px-4 py-3 text-center text-sm text-plum">
          {{ store.error }}
        </p>

        <div class="flex flex-wrap items-center justify-between gap-4 text-sm text-cocoa/70">
          <span>
            {{ turnLabel }}:
            <strong class="text-cocoa">{{ currentTurn }}</strong>
          </span>

          <div class="flex gap-2">
            <button
              type="button"
              class="rounded-full bg-mist px-5 py-2 text-sm font-semibold text-cocoa shadow-sm transition hover:bg-mist/70 disabled:opacity-60"
              :disabled="store.isLoading"
              @click="store.resetGame"
            >
              {{ refreshButtonLabel }}
            </button>

            <button
              type="button"
              class="rounded-full border border-plum/20 bg-plum/90 px-5 py-2 text-sm font-semibold text-white shadow-lg transition hover:-translate-y-0.5 disabled:opacity-60"
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
        role="status"
        aria-live="polite"
      >
        {{ toastText }}
      </div>
    </transition>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref } from "vue";

import Board from "~/components/Board.vue";
import ResultModal from "~/components/ResultModal.vue";
import { useGameStore } from "~/stores/game";

const store = useGameStore();

const copied = ref(false);
let toastTimer: ReturnType<typeof setTimeout> | null = null;

const heroBadge = "Уютный челлендж";
const heroTitle = "Твоя уютная TicTacToe-вселенная";
const heroDescription =
  "Сыграй против дружелюбного AI: он любит высчитанные ходы, но не способен спрятаться от твоей интуиции.";
const hintChipLabel = "Подсказка";

const instructionLines = [
  "X — твой символ, полный уверенности",
  "O — решимость компьютера",
  "Пустая клетка — место для нового микро-подвига",
];

const turnLabel = "Чей ход";
const playerTurnLabel = "Ты";
const computerTurnLabel = "Компьютер";
const aiThinkingLabel = "ИИ думает...";
const noTurnLabel = "Партия завершена";

const refreshButtonLabel = "Обновить поле";
const playAgainButtonLabel = "Сыграть ещё раз";
const toastText = "Промокод скопирован!";

const boardDisabled = computed(() => store.isBoardLocked || store.isLoading);

const statusHint = computed(() => {
  if (store.status === "win") return "Забери промокод";
  if (store.status === "lose") return "Попробуй новую тактику";
  if (store.status === "draw") return "Честная ничья";
  return "Следи за шагами AI";
});

const boardCaption = computed(() => {
  if (store.status === "win") return "Поле ждёт новую стратегию, которая так же мягка.";
  if (store.status === "lose") return "Реванш уже рядом: компьютер всего лишь несколько ходов вперёд.";
  if (store.status === "draw") return "Силы равны — нажми сброс и задай новую лёгкую стратегию.";
  return "Выбери клетку, чтобы сделать мягкий первый ход.";
});

const currentTurn = computed(() => {
  if (store.hasResult) return noTurnLabel;

  // Пока идёт запрос на /move — считаем, что «думает» ИИ
  if (store.isLoading) return aiThinkingLabel;

  if (store.next === "player") return playerTurnLabel;
  if (store.next === "computer") return computerTurnLabel;

  return noTurnLabel;
});

const onSelect = (index: number) => {
  if (boardDisabled.value) return;
  store.playerMove(index);
};

async function copyPromo() {
  if (!store.promoCode) return;

  try {
    // modern clipboard API
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(store.promoCode);
    } else {
      // fallback
      const el = document.createElement("textarea");
      el.value = store.promoCode;
      el.setAttribute("readonly", "");
      el.style.position = "absolute";
      el.style.left = "-9999px";
      document.body.appendChild(el);
      el.select();
      document.execCommand("copy");
      document.body.removeChild(el);
    }

    copied.value = true;
    if (toastTimer) clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      copied.value = false;
      toastTimer = null;
    }, 1500);
  } catch {
    // ignore
  }
}

onMounted(() => {
  store.bootstrap();
});

onBeforeUnmount(() => {
  if (toastTimer) clearTimeout(toastTimer);
});
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
