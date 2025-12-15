<template>
  <button
    class="relative flex h-20 items-center justify-center rounded-2xl border border-lilac/40 bg-white/80 shadow-inner transition hover:-translate-y-0.5 hover:shadow-xl disabled:opacity-60"
    :class="{ 'pointer-events-none': disabled || !!value }"
    type="button"
    :disabled="disabled || !!value"
    @click="emit('select')"
  >
    <span
      class="text-4xl font-serif transition-all duration-300"
      :class="value === 'X' ? 'text-cocoa scale-100' : value === 'O' ? 'text-plum scale-100' : 'scale-0'"
    >
      {{ value }}
    </span>
  </button>
</template>

<script setup lang="ts">
const props = defineProps<{ value: string; disabled: boolean }>()
const emit = defineEmits<{ select: [] }>()
</script>
