<template>
  <div class="page">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4 class="mb-0 fw-semibold">My Applications</h4>
      <button class="btn btn-success btn-sm" :disabled="exporting" @click="exportCSV">
        <span v-if="exporting" class="spinner-border spinner-border-sm me-2"></span>
        <i v-else class="bi bi-download me-1"></i>
        {{ exporting ? 'Exporting…' : 'Export CSV' }}
      </button>
    </div>

    <!-- Export status banner -->
    <div v-if="exportMsg" class="alert alert-info py-2 small">
      <i class="bi bi-info-circle me-1"></i>{{ exportMsg }}
    </div>

    <!-- Status filter -->
    <div class="row g-2 mb-3">
      <div class="col-md-3">
        <select v-model="statusFilter" class="form-select">
          <option value="">All statuses</option>
          <option value="applied">Applied</option>
          <option value="shortlisted">Shortlisted</option>
          <option value="interview">Interview</option>
          <option value="selected">Selected</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="spinner-center">
      <div class="spinner-border text-success"></div>
    </div>

    <div v-else-if="!filtered.length" class="text-center text-secondary py-5">
      <i class="bi bi-file-earmark-text fs-1"></i>
      <p class="mt-2">No applications yet</p>
      <RouterLink to="/student/drives" class="btn btn-success btn-sm mt-2">Browse drives</RouterLink>
    </div>

    <div v-else class="card p-0 overflow-hidden">
      <div class="table-responsive">
        <table class="table table-hover mb-0">
          <thead class="table-dark">
            <tr>
              <th>Drive</th>
              <th>Company</th>
              <th>Applied</th>
              <th>Interview</th>
              <th>Status</th>
              <th>Feedback</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in filtered" :key="a.id">
              <td>
                <RouterLink :to="`/student/drives/${a.drive_id}`" class="fw-semibold text-success text-decoration-none">
                  {{ a.drive_title }}
                </RouterLink>
              </td>
              <td>{{ a.company_name }}</td>
              <td>{{ fmtDate(a.applied_at) }}</td>
              <td>{{ a.interview_date ? fmtDate(a.interview_date) : '—' }}</td>
              <td><span :class="statusBadge(a.status)">{{ a.status }}</span></td>
              <td class="text-secondary small" style="max-width:200px">
                {{ a.company_feedback || '—' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../../main.js'

const applications = ref([])
const loading      = ref(false)
const statusFilter = ref('')
const exporting    = ref(false)
const exportMsg    = ref('')

onMounted(async () => {
  loading.value = true
  try { applications.value = await api('/student/applications') }
  catch (e) { alert('Failed to load applications: ' + e.message) }
  finally { loading.value = false }
})

const filtered = computed(() =>
  statusFilter.value
    ? applications.value.filter(a => a.status === statusFilter.value)
    : applications.value
)

async function exportCSV() {
  exporting.value = true
  exportMsg.value = 'Starting CSV export…'
  try {
    const data = await api('/student/export-csv', { method: 'POST' })
    exportMsg.value = data.message || 'Export started! Check your email (MailHog) shortly.'
    // Poll every 3 seconds to check if the Celery task finished
    if (data.task_id) pollExport(data.task_id)
  } catch (e) {
    exportMsg.value = 'Export failed: ' + e.message
  } finally {
    exporting.value = false
  }
}

function pollExport(taskId) {
  let tries = 0
  const interval = setInterval(async () => {
    tries++
    try {
      const data = await api(`/student/export-status/${taskId}`)
      if (data.state === 'SUCCESS') {
        exportMsg.value = '✓ CSV export complete! Check your email in MailHog (http://localhost:8025).'
        clearInterval(interval)
      } else if (data.state === 'FAILURE' || tries > 20) {
        exportMsg.value = tries > 20
          ? 'Export is taking long — check MailHog in a moment.'
          : 'Export failed. Try again.'
        clearInterval(interval)
      }
    } catch { clearInterval(interval) }
  }, 3000)
}

function statusBadge(s) {
  return { applied:'badge bg-primary', shortlisted:'badge bg-info text-dark',
           interview:'badge bg-warning text-dark', selected:'badge bg-success',
           rejected:'badge bg-danger' }[s] || 'badge bg-secondary'
}
function fmtDate(d) {
  return d ? new Date(d).toLocaleDateString('en-IN', { day:'numeric', month:'short', year:'numeric' }) : '—'
}
</script>
