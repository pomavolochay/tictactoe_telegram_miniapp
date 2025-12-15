<template>
  <div class="grid grid-cols-3 gap-3">
    <Cell
      v-for="(cell, index) in cells"
      :key="index"
      :value="cell"
      :disabled="disabled"
      @select="() => emit('select', index)"
    />
  </div>
</template>

<script setup lang="ts">
import Cell from './Cell.vue'

const props = defineProps<{ cells: string[]; disabled: boolean }>()
const emit = defineEmits<{ select: [index: number] }>()
</script>
