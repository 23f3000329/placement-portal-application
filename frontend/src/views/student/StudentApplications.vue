<template>
  <div class="page">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px">
      <h2>My Applications</h2>
      <button class="btn btn-primary btn-sm" :disabled="exporting" @click="exportCSV">
        {{ exporting ? 'Exporting…' : '↓ Export CSV' }}
      </button>
    </div>

    <div v-if="exportMsg" style="background:var(--blue-bg);color:var(--blue-text);padding:10px 14px;border-radius:var(--radius);margin-bottom:14px;font-size:0.88rem">
      {{ exportMsg }}
    </div>

    <div class="search-bar">
      <select v-model="statusFilter">
        <option value="">All statuses</option>
        <option value="applied">Applied</option>
        <option value="shortlisted">Shortlisted</option>
        <option value="interview">Interview</option>
        <option value="selected">Selected</option>
        <option value="rejected">Rejected</option>
      </select>
    </div>

    <div v-if="loading" class="spinner"></div>

    <div v-else-if="!filtered.length" class="empty-state card">
      <div class="icon">📄</div>
      <p>No applications yet</p>
      <RouterLink to="/student/drives" class="btn btn-sm btn-primary" style="margin-top:12px">Browse drives</RouterLink>
    </div>

    <div v-else class="card" style="padding:0;overflow:hidden">
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Drive</th>
              <th>Company</th>
              <th>Type</th>
              <th>Applied</th>
              <th>Interview</th>
              <th>Status</th>
              <th>Feedback</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in filtered" :key="a.id">
              <td>
                <RouterLink :to="`/student/drives/${a.drive_id}`" style="font-weight:600">
                  {{ a.drive_title }}
                </RouterLink>
              </td>
              <td>{{ a.company_name }}</td>
              <td><span class="badge badge-gray">{{ a.drive?.job_type || '—' }}</span></td>
              <td>{{ fmtDate(a.applied_at) }}</td>
              <td>{{ a.interview_date ? fmtDate(a.interview_date) : '—' }}</td>
              <td><StatusBadge :status="a.status" /></td>
              <td style="max-width:200px">
                <span style="font-size:0.82rem;color:var(--text2)">{{ a.company_feedback || '—' }}</span>
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
import { studentAPI } from '@/services/api'
import { useToastStore } from '@/store/toast'
import StatusBadge from '@/components/common/StatusBadge.vue'

const toast        = useToastStore()
const applications = ref([])
const loading      = ref(false)
const statusFilter = ref('')
const exporting    = ref(false)
const exportMsg    = ref('')

onMounted(async () => {
  loading.value = true
  try { const { data } = await studentAPI.getApplications(); applications.value = data }
  catch { toast.error('Failed to load applications') }
  finally { loading.value = false }
})

const filtered = computed(() => {
  if (!statusFilter.value) return applications.value
  return applications.value.filter(a => a.status === statusFilter.value)
})

async function exportCSV() {
  exporting.value = true
  exportMsg.value = ''
  try {
    const { data } = await studentAPI.exportCSV()
    exportMsg.value = data.message
    toast.info('CSV export started — check your email shortly')
    // Poll for completion
    if (data.task_id) pollExport(data.task_id)
  } catch { toast.error('Export failed') }
  finally { exporting.value = false }
}

function pollExport(taskId) {
  let tries = 0
  const interval = setInterval(async () => {
    tries++
    try {
      const { data } = await studentAPI.exportStatus(taskId)
      if (data.state === 'SUCCESS') {
        exportMsg.value = '✓ CSV export complete! Check your email.'
        clearInterval(interval)
      } else if (data.state === 'FAILURE' || tries > 20) {
        clearInterval(interval)
      }
    } catch { clearInterval(interval) }
  }, 3000)
}

function fmtDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-IN', { day:'numeric', month:'short', year:'numeric' })
}
</script>