<template>
  <transition name="fade">
    <div
      v-if="visible"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-6"
      role="dialog"
      aria-modal="true"
      :aria-labelledby="titleId"
      :aria-describedby="descId"
      tabindex="-1"
      @keydown.esc.prevent="onReset"
    >
      <div
        class="w-full max-w-md rounded-[32px] bg-white/95 p-8 text-center shadow-2xl"
      >
        <p v-if="badge" class="text-sm uppercase tracking-[0.3em] text-plum/70">
          {{ badge }}
        </p>

        <h3 :id="titleId" class="mt-4 font-serif text-3xl text-cocoa">
          {{ title }}
        </h3>

        <p :id="descId" class="mt-3 text-cocoa/80">
          {{ description }}
        </p>

        <div
          v-if="status === 'win' && promoCode"
          class="mt-6 flex flex-col items-center gap-3"
        >
          <div
            class="rounded-2xl bg-mist px-6 py-4 text-3xl font-serif tracking-widest text-plum"
          >
            {{ promoCode }}
          </div>

          <button
            type="button"
            class="rounded-full border border-plum/20 bg-plum px-6 py-2 text-sm text-white shadow-lg"
            @click="onCopy"
            :aria-label="copyButtonAriaLabel"
          >
            {{ copyButtonLabel }}
          </button>
        </div>

        <div class="mt-8 flex flex-col gap-3">
          <button
            type="button"
            class="rounded-full bg-gradient-to-r from-petal to-lilac px-6 py-3 text-sm font-semibold text-cocoa shadow-lg"
            @click="onReset"
          >
            {{ resetButtonLabel }}
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { computed } from "vue";

type GameStatus = "idle" | "in_progress" | "win" | "lose" | "draw";

const props = withDefaults(
  defineProps<{
    visible: boolean;
    status: GameStatus;
    title: string;
    description: string;
    promoCode?: string | null;
  }>(),
  {
    promoCode: null,
    status: "idle",
  }
);

const emit = defineEmits<{
  reset: [];
  copy: [];
}>();

const copyButtonLabel =
  "\u0421\u043a\u043e\u043f\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u043a\u043e\u0434";
const resetButtonLabel =
  "\u0421\u044b\u0433\u0440\u0430\u0442\u044c \u0435\u0449\u0451 \u0440\u0430\u0437";
const copyButtonAriaLabel =
  "\u0421\u043a\u043e\u043f\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u043f\u0440\u043e\u043c\u043e\u043a\u043e\u0434";

const titleId = "result-modal-title";
const descId = "result-modal-desc";

const badge = computed(() => {
  switch (props.status) {
    case "win":
      return "\u041f\u043e\u0431\u0435\u0434\u0430";
    case "lose":
      return "\u041f\u043e\u0440\u0430\u0436\u0435\u043d\u0438\u0435";
    case "draw":
      return "\u041d\u0438\u0447\u044c\u044f";
    default:
      return "";
  }
});

function onReset() {
  emit("reset");
}

function onCopy() {
  emit("copy");
}
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
