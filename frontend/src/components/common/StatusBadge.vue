<template>
  <span :class="['badge', badgeClass]">{{ label }}</span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ status: String })

const map = {
  approved:    { cls: 'badge-green',  label: 'Approved' },
  active:      { cls: 'badge-green',  label: 'Active' },
  selected:    { cls: 'badge-green',  label: 'Selected' },
  pending:     { cls: 'badge-amber',  label: 'Pending' },
  shortlisted: { cls: 'badge-teal',   label: 'Shortlisted' },
  interview:   { cls: 'badge-blue',   label: 'Interview' },
  applied:     { cls: 'badge-blue',   label: 'Applied' },
  rejected:    { cls: 'badge-red',    label: 'Rejected' },
  closed:      { cls: 'badge-gray',   label: 'Closed' },
  blacklisted: { cls: 'badge-red',    label: 'Blacklisted' },
  inactive:    { cls: 'badge-gray',   label: 'Inactive' },
  open:        { cls: 'badge-green',  label: 'Open' },
}

const badgeClass = computed(() => map[props.status]?.cls || 'badge-gray')
const label      = computed(() => map[props.status]?.label || props.status)
</script>