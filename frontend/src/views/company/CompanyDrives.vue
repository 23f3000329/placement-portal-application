<template>
  <div class="page">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4 class="mb-0 fw-semibold">My Drives</h4>
      <button class="btn btn-success" @click="showForm = !showForm">
        <i :class="showForm ? 'bi bi-x-lg' : 'bi bi-plus-lg'" class="me-1"></i>
        {{ showForm ? 'Cancel' : 'Create Drive' }}
      </button>
    </div>

    <!-- Create drive form -->
    <div v-if="showForm" class="card mb-4">
      <div class="card-header fw-semibold">New Placement Drive</div>
      <div class="card-body">
        <div v-if="formError"   class="alert alert-danger  py-2">{{ formError }}</div>
        <div v-if="formSuccess" class="alert alert-success py-2">{{ formSuccess }}</div>

        <div class="mb-3">
          <label class="form-label">Job Title *</label>
          <input v-model="form.title" class="form-control" placeholder="e.g. Software Development Engineer" />
        </div>
        <div class="mb-3">
          <label class="form-label">Job Description</label>
          <textarea v-model="form.job_description" class="form-control" rows="4"
            placeholder="Role responsibilities, tech stack, culture…"></textarea>
        </div>

        <div class="row g-3 mb-3">
          <div class="col-md-6">
            <label class="form-label">Job Type</label>
            <select v-model="form.job_type" class="form-select">
              <option>Full-time</option><option>Internship</option><option>Contract</option>
            </select>
          </div>
          <div class="col-md-6">
            <label class="form-label">Interview Mode</label>
            <select v-model="form.interview_mode" class="form-select">
              <option>In-person</option><option>Virtual</option><option>Hybrid</option>
            </select>
          </div>
        </div>

        <div class="row g-3 mb-3">
          <div class="col-md-4">
            <label class="form-label">Min Salary (₹)</label>
            <input v-model.number="form.salary_min" type="number" class="form-control" placeholder="400000" />
          </div>
          <div class="col-md-4">
            <label class="form-label">Max Salary (₹)</label>
            <input v-model.number="form.salary_max" type="number" class="form-control" placeholder="800000" />
          </div>
          <div class="col-md-4">
            <label class="form-label">Min CGPA</label>
            <input v-model.number="form.min_cgpa" type="number" step="0.1" min="0" max="10" class="form-control" placeholder="7.5" />
          </div>
        </div>

        <div class="row g-3 mb-3">
          <div class="col-md-6">
            <label class="form-label">Location</label>
            <input v-model="form.location" class="form-control" placeholder="Bangalore" />
          </div>
          <div class="col-md-6">
            <label class="form-label">Application Deadline</label>
            <input v-model="form.application_deadline" type="date" class="form-control" />
          </div>
        </div>

        <div class="mb-3">
          <label class="form-label">Eligible Branches <small class="text-secondary">(click to select)</small></label>
          <div class="chip-group">
            <span v-for="b in allBranches" :key="b"
              :class="['chip', form.eligible_branches.includes(b) ? 'active' : '']"
              @click="toggleBranch(b)">{{ b }}</span>
          </div>
        </div>

        <div class="mb-3">
          <label class="form-label">Skills Required</label>
          <input v-model="form.skills_required" class="form-control" placeholder="Python, SQL, REST APIs" />
        </div>

        <div class="d-flex gap-2">
          <button class="btn btn-success" :disabled="saving" @click="submitDrive">
            <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
            {{ saving ? 'Submitting…' : 'Submit for admin approval' }}
          </button>
          <button class="btn btn-outline-secondary" @click="showForm = false">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Drive list -->
    <div v-if="loading" class="spinner-center"><div class="spinner-border text-success"></div></div>

    <div v-else-if="!drives.length && !showForm" class="text-center text-secondary py-5">
      <i class="bi bi-briefcase fs-1"></i>
      <p class="mt-2">No drives yet. Create your first drive to start recruiting.</p>
    </div>

    <div v-for="d in drives" :key="d.id" class="drive-card"
      @click="$router.push(`/company/drives/${d.id}/applicants`)">
      <div>
        <div class="fw-semibold">{{ d.title }}</div>
        <div class="text-secondary small mt-1">{{ d.job_type }} · {{ d.location || 'Remote' }}</div>
        <div class="d-flex flex-wrap gap-1 mt-2">
          <span v-if="d.salary_min" class="badge bg-secondary">
            ₹{{ fmtSalary(d.salary_min) }}{{ d.salary_max ? ' – ₹' + fmtSalary(d.salary_max) : '+' }}
          </span>
          <span class="badge bg-secondary">CGPA ≥ {{ d.min_cgpa || 'Any' }}</span>
          <span v-if="d.application_deadline" class="badge bg-secondary">
            Deadline: {{ fmtDate(d.application_deadline) }}
          </span>
        </div>
      </div>
      <div class="drive-actions">
        <span :class="statusBadge(d.status)">{{ d.status }}</span>
        <small class="text-secondary">{{ d.applications_count }} applicant(s)</small>
        <button class="btn btn-success btn-sm"
          @click.stop="$router.push(`/company/drives/${d.id}/applicants`)">
          <i class="bi bi-people me-1"></i>View applicants
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { api } from '../../main.js'

const drives      = ref([])
const loading     = ref(false)
const saving      = ref(false)
const showForm    = ref(false)
const formError   = ref('')
const formSuccess = ref('')
const allBranches = ['CSE','ECE','IT','DS','ME','EEE','Civil','Chemical']

const form = reactive({
  title:'', job_description:'', job_type:'Full-time', interview_mode:'In-person',
  salary_min:'', salary_max:'', min_cgpa:'', location:'', eligible_branches:[],
  skills_required:'', application_deadline:'',
})

onMounted(loadDrives)

async function loadDrives() {
  loading.value = true
  try { drives.value = await api('/company/drives') }
  catch (e) { alert('Failed to load drives: ' + e.message) }
  finally { loading.value = false }
}

function toggleBranch(b) {
  const i = form.eligible_branches.indexOf(b)
  i >= 0 ? form.eligible_branches.splice(i,1) : form.eligible_branches.push(b)
}

async function submitDrive() {
  formError.value = ''; formSuccess.value = ''
  if (!form.title) { formError.value = 'Job title is required'; return }
  saving.value = true
  try {
    await api('/company/drives', {
      method: 'POST',
      body: JSON.stringify({
        ...form,
        salary_min: form.salary_min || null, salary_max: form.salary_max || null,
        min_cgpa: form.min_cgpa || null,
        application_deadline: form.application_deadline ? new Date(form.application_deadline).toISOString() : null,
      })
    })
    formSuccess.value = '✓ Drive submitted for admin approval!'
    Object.assign(form, { title:'', job_description:'', salary_min:'', salary_max:'', min_cgpa:'',
      location:'', eligible_branches:[], skills_required:'', application_deadline:'',
      job_type:'Full-time', interview_mode:'In-person' })
    loadDrives()
    setTimeout(() => { showForm.value = false; formSuccess.value = '' }, 2000)
  } catch (e) { formError.value = e.message }
  finally { saving.value = false }
}

function statusBadge(s) {
  return { pending:'badge bg-warning text-dark', approved:'badge bg-success', rejected:'badge bg-danger', closed:'badge bg-secondary' }[s] || 'badge bg-secondary'
}
function fmtSalary(v) { return v >= 100000 ? (v/100000).toFixed(1)+'L' : v?.toLocaleString() }
function fmtDate(d) { return d ? new Date(d).toLocaleDateString('en-IN', { day:'numeric', month:'short', year:'numeric' }) : '—' }
</script>
