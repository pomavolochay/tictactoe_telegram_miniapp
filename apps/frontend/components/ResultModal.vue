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
      @click.self="onReset"
      ref="overlayRef"
    >
      <div class="w-full max-w-md rounded-[32px] bg-white/95 p-8 text-center shadow-2xl">
        <p v-if="badge" class="text-sm uppercase tracking-[0.3em] text-plum/70">
          {{ badge }}
        </p>

        <h3 :id="titleId" class="mt-4 font-serif text-3xl text-cocoa">
          {{ title }}
        </h3>

        <p :id="descId" class="mt-3 text-cocoa/80">
          {{ description }}
        </p>

        <div v-if="status === 'win' && promoCode" class="mt-6 flex flex-col items-center gap-3">
          <div class="rounded-2xl bg-mist px-6 py-4 text-3xl font-serif tracking-widest text-plum">
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
            ref="primaryButtonRef"
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
import { computed, nextTick, ref, watch } from "vue";
import { useId } from "#imports";

type GameStatus = "in_progress" | "win" | "lose" | "draw";

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
  }
);

const emit = defineEmits<{
  reset: [];
  copy: [];
}>();

const copyButtonLabel = "Скопировать код";
const resetButtonLabel = "Сыграть ещё раз";
const copyButtonAriaLabel = "Скопировать промокод";

const uid = useId();
const titleId = `result-modal-title-${uid}`;
const descId = `result-modal-desc-${uid}`;

const overlayRef = ref<HTMLDivElement | null>(null);
const primaryButtonRef = ref<HTMLButtonElement | null>(null);

const badge = computed(() => {
  switch (props.status) {
    case "win":
      return "Победа";
    case "lose":
      return "Поражение";
    case "draw":
      return "Ничья";
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

// Фокус при открытии: сначала на основную кнопку, иначе на overlay
watch(
  () => props.visible,
  async (v) => {
    if (!v) return;
    await nextTick();
    primaryButtonRef.value?.focus?.();
    if (document.activeElement !== primaryButtonRef.value) {
      overlayRef.value?.focus?.();
    }
  }
);
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
