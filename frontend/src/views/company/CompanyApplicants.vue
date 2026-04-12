<template>
  <div class="page">
    <div class="d-flex align-items-center gap-3 mb-4">
      <button class="btn btn-outline-secondary btn-sm" @click="$router.back()">
        <i class="bi bi-arrow-left"></i> Back
      </button>
      <h4 class="mb-0 fw-semibold">{{ driveName || 'Applicants' }}</h4>
    </div>

    <div class="row g-2 mb-3">
      <div class="col-md-5">
        <input v-model="query" class="form-control" placeholder="Search by name or branch…" />
      </div>
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

    <div v-if="loading" class="spinner-center"><div class="spinner-border text-success"></div></div>

    <div v-else-if="!filtered.length" class="text-center text-secondary py-5">
      <i class="bi bi-file-person fs-1"></i><p class="mt-2">No applications match your filters</p>
    </div>

    <div v-else class="card p-0 overflow-hidden">
      <div class="table-responsive">
        <table class="table table-hover mb-0">
          <thead class="table-dark">
            <tr>
              <th>Student</th><th>Branch</th><th>CGPA</th><th>Applied</th>
              <th>Status</th><th>Update Status</th><th>Interview Date</th><th>Feedback</th><th>Resume</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in filtered" :key="a.id">
              <td>
                <div class="fw-semibold">{{ a.student_name }}</div>
                <small class="text-secondary">{{ a.student_email }}</small>
              </td>
              <td>{{ a.student_branch || '—' }}</td>
              <td>{{ a.student_cgpa ?? '—' }}</td>
              <td>{{ fmtDate(a.applied_at) }}</td>
              <td><span :class="statusBadge(a.status)">{{ a.status }}</span></td>
              <td>
                <select class="form-select form-select-sm" style="width:140px"
                  :value="a.status" @change="updateStatus(a, $event.target.value)">
                  <option value="applied">Applied</option>
                  <option value="shortlisted">Shortlisted</option>
                  <option value="interview">Interview</option>
                  <option value="selected">Selected</option>
                  <option value="rejected">Rejected</option>
                </select>
              </td>
              <td>
                <input type="date" class="form-control form-control-sm" style="width:155px"
                  :value="a.interview_date ? a.interview_date.slice(0,10) : ''"
                  @change="updateInterview(a, $event.target.value)" />
              </td>
              <td>
                <input type="text" class="form-control form-control-sm" style="width:180px"
                  :value="a.company_feedback || ''" placeholder="Add feedback…"
                  @blur="updateFeedback(a, $event.target.value)" />
              </td>
              <td>
                <!-- Resume view: token passed as query param because browser tabs
                     cannot send Authorization headers, only fetch() can. -->
                <a v-if="a.student_resume"
                  :href="`/api/student/resume/${a.student_resume}?token=${getToken()}`"
                  target="_blank"
                  class="btn btn-outline-secondary btn-sm">
                  <i class="bi bi-file-earmark-person"></i> View Resume
                </a>
                <span v-else class="text-secondary small">No resume</span>
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
import { api, getToken } from '../../main.js'

const route        = useRoute()
const driveId      = Number(route.params.id)
const applications = ref([])
const driveName    = ref('')
const loading      = ref(false)
const query        = ref('')
const statusFilter = ref('')

onMounted(async () => {
  loading.value = true
  try {
    const [apps, drives] = await Promise.all([
      api(`/company/drives/${driveId}/applications`),
      api('/company/drives'),
    ])
    applications.value = apps
    const drive = drives.find(d => d.id === driveId)
    if (drive) driveName.value = drive.title
  } catch (e) { alert('Failed to load applicants: ' + e.message) }
  finally { loading.value = false }
})

const filtered = computed(() => {
  let list = applications.value
  if (statusFilter.value) list = list.filter(a => a.status === statusFilter.value)
  if (query.value) {
    const q = query.value.toLowerCase()
    list = list.filter(a => a.student_name?.toLowerCase().includes(q) || a.student_branch?.toLowerCase().includes(q))
  }
  return list
})

async function updateStatus(app, newStatus) {
  try {
    Object.assign(
      app,
      await api(`/company/applications/${app.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ status: newStatus })
      })
    )
  } catch (e) {
    alert('Update failed: ' + e.message)
  }
}

async function updateInterview(app, dateStr) {
  if (!dateStr) return

  try {
    Object.assign(
      app,
      await api(`/company/applications/${app.id}`, {
        method: 'PATCH',
        body: JSON.stringify({
          interview_date: new Date(dateStr).toISOString()
        })
      })
    )
  } catch (e) {
    alert('Update failed: ' + e.message)
  }
}

async function updateFeedback(app, feedback) {
  if (feedback === (app.company_feedback || '')) return

  try {
    Object.assign(
      app,
      await api(`/company/applications/${app.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ company_feedback: feedback })
      })
    )
  } catch (e) {
    alert('Update failed: ' + e.message)
  }
}

function statusBadge(s) {
  return {
    applied: 'badge bg-primary',
    shortlisted: 'badge bg-info text-dark',
    interview: 'badge bg-warning text-dark',
    selected: 'badge bg-success',
    rejected: 'badge bg-danger'
  }[s] || 'badge bg-secondary'
}

function fmtDate(d) {
  return d
    ? new Date(d).toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
      })
    : '—'
}
</script>