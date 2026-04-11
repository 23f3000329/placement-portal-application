<template>
  <div class="page">
    <button class="btn btn-outline-secondary btn-sm mb-4" @click="$router.back()">
      <i class="bi bi-arrow-left me-1"></i>Back
    </button>

    <div v-if="loading" class="spinner-center">
      <div class="spinner-border text-success"></div>
    </div>

    <template v-else-if="drive">
      <div class="row g-4">

        <!-- Left: drive details -->
        <div class="col-lg-8">
          <div class="card mb-3">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start mb-3">
                <div>
                  <h5 class="fw-semibold mb-1">{{ drive.title }}</h5>
                  <div class="text-secondary">{{ drive.company_name }}</div>
                </div>
                <span :class="statusBadge(drive.status)">{{ drive.status }}</span>
              </div>

              <div class="d-flex flex-wrap gap-2 mb-3">
                <span class="badge bg-secondary">{{ drive.job_type }}</span>
                <span class="badge bg-secondary">{{ drive.location || 'Remote' }}</span>
                <span class="badge bg-secondary">{{ drive.interview_mode }}</span>
                <span v-if="drive.salary_min" class="badge bg-secondary">
                  ₹{{ fmtSalary(drive.salary_min) }}{{ drive.salary_max ? ' – ₹' + fmtSalary(drive.salary_max) : '+' }} p.a.
                </span>
              </div>

              <div class="mb-3">
                <div class="section-label">Job Description</div>
                <p class="small lh-lg" style="white-space:pre-wrap">
                  {{ drive.job_description || 'No description provided.' }}
                </p>
              </div>

              <div v-if="drive.skills_required">
                <div class="section-label">Skills Required</div>
                <div class="d-flex flex-wrap gap-1">
                  <span v-for="s in drive.skills_required.split(',')" :key="s"
                    class="badge bg-secondary">{{ s.trim() }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Eligibility criteria -->
          <div class="card">
            <div class="card-header fw-semibold">Eligibility criteria</div>
            <ul class="list-group list-group-flush">
              <li class="list-group-item d-flex justify-content-between">
                <span class="text-secondary">Minimum CGPA</span>
                <span class="fw-semibold">{{ drive.min_cgpa || 'None' }}</span>
              </li>
              <li class="list-group-item d-flex justify-content-between align-items-center">
                <span class="text-secondary">Eligible branches</span>
                <span v-if="!drive.eligible_branches?.length">All branches</span>
                <div v-else class="d-flex flex-wrap gap-1 justify-content-end">
                  <span v-for="b in drive.eligible_branches" :key="b" class="badge bg-secondary">{{ b }}</span>
                </div>
              </li>
              <li class="list-group-item d-flex justify-content-between">
                <span class="text-secondary">Application deadline</span>
                <span class="fw-semibold"
                  :class="isDeadlineSoon(drive.application_deadline) ? 'text-danger' : ''">
                  {{ fmtDate(drive.application_deadline) || 'Open' }}
                  <span v-if="isDeadlineSoon(drive.application_deadline)">⚠ Closing soon</span>
                </span>
              </li>
            </ul>
          </div>
        </div>

        <!-- Right: apply card -->
        <div class="col-lg-4">

          <!-- Already applied -->
          <div v-if="drive.already_applied && drive.application" class="card">
            <div class="card-header fw-semibold">Your application</div>
            <div class="card-body">
              <div class="mb-3">
                <div class="section-label">Status</div>
                <span :class="statusBadge(drive.application.status)">{{ drive.application.status }}</span>
              </div>
              <div v-if="drive.application.interview_date" class="mb-3">
                <div class="section-label">Interview date</div>
                <div class="fw-semibold">{{ fmtDate(drive.application.interview_date) }}</div>
              </div>
              <div v-if="drive.application.company_feedback" class="mb-3">
                <div class="section-label">Feedback</div>
                <p class="small mb-0">{{ drive.application.company_feedback }}</p>
              </div>
              <div class="text-secondary small">
                Applied {{ fmtDate(drive.application.applied_at) }}
              </div>
            </div>
          </div>

          <!-- Not yet applied -->
          <div v-else class="card">
            <div class="card-header fw-semibold">Apply for this drive</div>
            <div class="card-body">
              <div v-if="!drive.is_eligible" class="alert alert-danger py-2 small">
                <i class="bi bi-x-circle me-1"></i>You don't meet the eligibility criteria.
              </div>
              <div v-else class="alert alert-success py-2 small">
                <i class="bi bi-check-circle me-1"></i>You meet the eligibility criteria.
              </div>

              <p class="text-secondary small mb-3">
                Your profile will be shared with {{ drive.company_name }}.
              </p>

              <div v-if="applyError"   class="alert alert-danger  py-2 small mb-2">{{ applyError }}</div>
              <div v-if="applySuccess" class="alert alert-success py-2 small mb-2">{{ applySuccess }}</div>

              <button class="btn btn-success w-100"
                :disabled="!drive.is_eligible || applying"
                @click="applyNow">
                <span v-if="applying" class="spinner-border spinner-border-sm me-2"></span>
                {{ applying ? 'Submitting…' : 'Apply now' }}
              </button>
            </div>
          </div>

        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../../main.js'

const route        = useRoute()
const router       = useRouter()
const drive        = ref(null)
const loading      = ref(false)
const applying     = ref(false)
const applyError   = ref('')
const applySuccess = ref('')

onMounted(async () => {
  loading.value = true
  try { drive.value = await api(`/student/drives/${route.params.id}`) }
  catch (e) { alert('Drive not found'); router.push('/student/drives') }
  finally { loading.value = false }
})

async function applyNow() {
  applyError.value = ''; applySuccess.value = ''
  applying.value = true
  try {
    await api(`/student/apply/${drive.value.id}`, { method: 'POST' })
    applySuccess.value = '✓ Application submitted successfully!'
    drive.value = await api(`/student/drives/${drive.value.id}`)
  } catch (e) { applyError.value = e.message }
  finally { applying.value = false }
}

function isDeadlineSoon(d) { return d && (new Date(d) - new Date()) < 3 * 86400000 }
function fmtSalary(v) { return v >= 100000 ? (v / 100000).toFixed(1) + 'L' : v?.toLocaleString() }
function fmtDate(d) { return d ? new Date(d).toLocaleDateString('en-IN', { day:'numeric', month:'short', year:'numeric' }) : '' }
function statusBadge(s) {
  return {
    approved:'badge bg-success', pending:'badge bg-warning text-dark',
    rejected:'badge bg-danger',  closed:'badge bg-secondary',
    applied:'badge bg-primary',  shortlisted:'badge bg-info text-dark',
    interview:'badge bg-warning text-dark', selected:'badge bg-success'
  }[s] || 'badge bg-secondary'
}
</script>

<style scoped>
.section-label {
  font-size: 0.72rem; font-weight: 600; color: var(--bs-secondary-color);
  text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.4rem;
}
</style>
