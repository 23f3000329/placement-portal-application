<template>
  <div class="page">
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px">
      <button class="btn btn-sm" @click="$router.back()">← Back</button>
      <h2>{{ drive?.title || 'Applicants' }}</h2>
      <StatusBadge v-if="drive" :status="drive.status" />
    </div>

    <div v-if="drive" style="display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap">
      <span class="pill">{{ drive.company_name }}</span>
      <span class="pill">{{ drive.job_type }}</span>
      <span class="pill">Min CGPA {{ drive.min_cgpa }}</span>
      <span class="pill">{{ drive.applications_count }} applicant(s)</span>
    </div>

    <!-- Filter -->
    <div class="search-bar">
      <input v-model="query" placeholder="Search by name or branch…" />
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
      <div class="icon">📄</div><p>No applications match your filters</p>
    </div>

    <div v-else class="card" style="padding:0;overflow:hidden">
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Student</th>
              <th>Branch</th>
              <th>CGPA</th>
              <th>Applied</th>
              <th>Interview</th>
              <th>Status</th>
              <th>Update status</th>
              <th>Schedule interview</th>
              <th>Feedback</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in filtered" :key="a.id">
              <td>
                <div style="font-weight:600">{{ a.student_name }}</div>
                <small>{{ a.student_email }}</small>
              </td>
              <td>{{ a.student_branch || '—' }}</td>
              <td>{{ a.student_cgpa ?? '—' }}</td>
              <td>{{ fmtDate(a.applied_at) }}</td>
              <td>{{ a.interview_date ? fmtDate(a.interview_date) : '—' }}</td>
              <td><StatusBadge :status="a.status" /></td>
              <td>
                <select
                  class="form-control"
                  style="width:140px;padding:4px 8px;font-size:0.8rem"
                  :value="a.status"
                  @change="updateStatus(a, $event.target.value)"
                >
                  <option value="applied">Applied</option>
                  <option value="shortlisted">Shortlisted</option>
                  <option value="interview">Interview</option>
                  <option value="selected">Selected</option>
                  <option value="rejected">Rejected</option>
                </select>
              </td>
              <td>
                <input
                  type="date"
                  class="form-control"
                  style="width:150px;padding:4px 8px;font-size:0.8rem"
                  :value="a.interview_date ? a.interview_date.split('T')[0] : ''"
                  @change="updateInterview(a, $event.target.value)"
                />
              </td>
              <td>
                <input
                  type="text"
                  class="form-control"
                  style="width:180px;padding:4px 8px;font-size:0.8rem"
                  :value="a.company_feedback || ''"
                  placeholder="Add feedback…"
                  @blur="updateFeedback(a, $event.target.value)"
                />
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
import { useRoute } from 'vue-router'
import { companyAPI, adminAPI } from '@/services/api'
import { useToastStore } from '@/store/toast'
import StatusBadge from '@/components/common/StatusBadge.vue'

const route        = useRoute()
const toast        = useToastStore()
const applications = ref([])
const drive        = ref(null)
const loading      = ref(false)
const query        = ref('')
const statusFilter = ref('')
const driveId      = +route.params.id

onMounted(async () => {
  loading.value = true
  try {
    const [aRes, dRes] = await Promise.all([
      companyAPI.getDriveApps(driveId),
      companyAPI.getDrives(),
    ])
    applications.value = aRes.data
    drive.value = dRes.data.find(d => d.id === driveId)
  } catch { toast.error('Failed to load applicants') }
  finally { loading.value = false }
})

const filtered = computed(() => {
  let list = applications.value
  if (statusFilter.value) list = list.filter(a => a.status === statusFilter.value)
  if (query.value) {
    const q = query.value.toLowerCase()
    list = list.filter(a =>
      a.student_name?.toLowerCase().includes(q) ||
      a.student_branch?.toLowerCase().includes(q)
    )
  }
  return list
})

async function updateStatus(app, status) {
  try {
    const { data } = await companyAPI.updateApplication(app.id, { status })
    Object.assign(app, data)
    toast.success(`Status updated to ${status}`)
  } catch { toast.error('Update failed') }
}

async function updateInterview(app, date) {
  if (!date) return
  try {
    const { data } = await companyAPI.updateApplication(app.id, {
      interview_date: new Date(date).toISOString()
    })
    Object.assign(app, data)
    toast.success('Interview date set')
  } catch { toast.error('Update failed') }
}

async function updateFeedback(app, feedback) {
  if (feedback === (app.company_feedback || '')) return
  try {
    const { data } = await companyAPI.updateApplication(app.id, { company_feedback: feedback })
    Object.assign(app, data)
  } catch { toast.error('Update failed') }
}

function fmtDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-IN', { day:'numeric', month:'short', year:'numeric' })
}
</script>