<template>
  <div class="page">
    <h4 class="mb-4 fw-semibold">All Applications</h4>

    <div v-if="loading" class="spinner-center"><div class="spinner-border text-success"></div></div>

    <div v-else-if="!applications.length" class="text-center text-secondary py-5">
      <i class="bi bi-file-earmark-text fs-1"></i><p class="mt-2">No applications yet</p>
    </div>

    <div v-else class="card p-0 overflow-hidden">
      <table class="table table-hover mb-0">
        <thead class="table-dark">
          <tr><th>Student</th><th>Drive</th><th>Company</th><th>Date</th><th>Status</th></tr>
        </thead>
        <tbody>
          <tr v-for="a in applications" :key="a.id">
            <td class="fw-semibold">{{ a.student_name }}</td>
            <td>{{ a.drive_title }}</td>
            <td>{{ a.company_name }}</td>
            <td>{{ fmtDate(a.applied_at) }}</td>
            <td><span :class="statusBadge(a.status)">{{ a.status }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../../main.js'

const applications = ref([])
const loading      = ref(false)

onMounted(async () => {
  loading.value = true
  try { applications.value = await api('/admin/applications') }
  catch (e) { alert(e.message) }
  finally { loading.value = false }
})

function statusBadge(s) {
  return { applied:'badge bg-primary', shortlisted:'badge bg-info text-dark', interview:'badge bg-warning text-dark', selected:'badge bg-success', rejected:'badge bg-danger' }[s] || 'badge bg-secondary'
}
function fmtDate(d) { return d ? new Date(d).toLocaleDateString('en-IN', { day:'numeric', month:'short', year:'numeric' }) : '—' }
</script>
