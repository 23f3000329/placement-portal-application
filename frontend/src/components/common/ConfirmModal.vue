<template>
  <div class="modal-overlay" @click.self="$emit('cancel')">
    <div class="modal" style="max-width:400px">
      <div class="modal-header">
        <h3>{{ title }}</h3>
        <button class="btn btn-sm btn-icon" @click="$emit('cancel')">✕</button>
      </div>
      <p style="color:var(--text2);font-size:0.9rem;margin-bottom:20px">{{ message }}</p>
      <div style="display:flex;gap:8px;justify-content:flex-end">
        <button class="btn" @click="$emit('cancel')">Cancel</button>
        <button :class="['btn', confirmClass]" @click="$emit('confirm')">{{ confirmLabel }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title:        { type: String, default: 'Confirm action' },
  message:      { type: String, default: 'Are you sure?' },
  confirmLabel: { type: String, default: 'Confirm' },
  confirmClass: { type: String, default: 'btn-danger' },
})
defineEmits(['confirm', 'cancel'])
</script>