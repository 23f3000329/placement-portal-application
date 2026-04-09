<template>
  <div class="toast-container">
    <div
      v-for="t in toastStore.toasts"
      :key="t.id"
      :class="['toast', `toast-${t.type}`]"
    >
      <span>{{ t.type === 'success' ? '✓' : t.type === 'error' ? '✕' : 'ℹ' }}</span>
      <span>{{ t.message }}</span>
    </div>
  </div>
</template>

<script setup>
import { useToastStore } from '@/store/toast'
const toastStore = useToastStore()
</script>