<template>
  <div class="page">
    <h4 class="mb-4 fw-semibold">Dashboard</h4>

    <div v-if="loading" class="spinner-center"><div class="spinner-border text-success"></div></div>

    <template v-else>
      <div class="row g-3 mb-4">
        <div class="col-sm-6 col-xl-3">
          <div class="card text-center p-3">
            <div class="stat-num text-primary">{{ stats.total_drives }}</div>
            <div class="stat-label">Total Drives</div>
          </div>
        </div>
        <div class="col-sm-6 col-xl-3">
          <div class="card text-center p-3">
            <div class="stat-num text-success">{{ stats.total_applicants }}</div>
            <div class="stat-label">Applicants</div>
          </div>
        </div>
        <div class="col-sm-6 col-xl-3">
          <div class="card text-center p-3">
            <div class="stat-num text-warning">{{ stats.shortlisted }}</div>
            <div class="stat-label">Shortlisted</div>
          </div>
        </div>
        <div class="col-sm-6 col-xl-3">
          <div class="card text-center p-3">
            <div class="stat-num text-info">{{ stats.selected }}</div>
            <div class="stat-label">Selected</div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
          <span class="fw-semibold">Recent drives</span>
          <RouterLink to="/company/drives" class="btn btn-outline-success btn-sm">View all →</RouterLink>
        </div>
        <div v-if="!drives.length" class="text-center text-secondary py-4">
          <p>No drives yet. <RouterLink to="/company/drives" class="text-success">Create one →</RouterLink></p>
        </div>
        <ul v-else class="list-group list-group-flush">
          <li v-for="d in drives.slice(0,5)" :key="d.id"
            class="list-group-item d-flex justify-content-between align-items-center">
            <div>
              <div class="fw-semibold">{{ d.title }}</div>
              <small class="text-secondary">{{ d.applications_count }} applicants · Deadline: {{ fmtDate(d.application_deadline) }}</small>
            </div>
            <span :class="statusBadge(d.status)">{{ d.status }}</span>
          </li>
        </ul>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../../main.js'

const loading = ref(true)
const stats   = ref({ total_drives:0, total_applicants:0, shortlisted:0, selected:0 })
const drives  = ref([])

onMounted(async () => {
  try {
    const [statsData, drivesData] = await Promise.all([api('/company/stats'), api('/company/drives')])
    stats.value  = statsData
    drives.value = drivesData
  } catch (e) { alert('Failed to load dashboard: ' + e.message) }
  finally { loading.value = false }
})

function statusBadge(s) {
  return { pending:'badge bg-warning text-dark', approved:'badge bg-success', rejected:'badge bg-danger', closed:'badge bg-secondary' }[s] || 'badge bg-secondary'
}
function fmtDate(d) { return d ? new Date(d).toLocaleDateString('en-IN', { day:'numeric', month:'short', year:'numeric' }) : '—' }
</script>
