<template>
  <div class="page">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px">
      <h2>My Drives</h2>
      <button class="btn btn-primary" @click="showForm = !showForm">
        {{ showForm ? '✕ Cancel' : '+ Create Drive' }}
      </button>
    </div>

    <!-- Create form -->
    <div v-if="showForm" class="card" style="margin-bottom:20px">
      <h3 style="margin-bottom:16px">New Placement Drive</h3>
      <div class="form-group">
        <label>Job title *</label>
        <input v-model="form.title" class="form-control" placeholder="e.g. Software Development Engineer" />
      </div>
      <div class="form-group">
        <label>Job description</label>
        <textarea v-model="form.job_description" class="form-control" placeholder="Role responsibilities, tech stack, culture…"></textarea>
      </div>
      <div class="form-grid-2">
        <div class="form-group">
          <label>Job type</label>
          <select v-model="form.job_type" class="form-control">
            <option>Full-time</option><option>Internship</option><option>Contract</option>
          </select>
        </div>
        <div class="form-group">
          <label>Interview mode</label>
          <select v-model="form.interview_mode" class="form-control">
            <option>In-person</option><option>Virtual</option><option>Hybrid</option>
          </select>
        </div>
      </div>
      <div class="form-grid-3">
        <div class="form-group">
          <label>Min salary (₹)</label>
          <input v-model="form.salary_min" type="number" class="form-control" placeholder="400000" />
        </div>
        <div class="form-group">
          <label>Max salary (₹)</label>
          <input v-model="form.salary_max" type="number" class="form-control" placeholder="800000" />
        </div>
        <div class="form-group">
          <label>Min CGPA</label>
          <input v-model="form.min_cgpa" type="number" step="0.1" min="0" max="10" class="form-control" placeholder="7.5" />
        </div>
      </div>
      <div class="form-group">
        <label>Location</label>
        <input v-model="form.location" class="form-control" placeholder="Bangalore" />
      </div>
      <div class="form-group">
        <label>Eligible branches</label>
        <div class="chip-group">
          <span
            v-for="b in allBranches" :key="b"
            :class="['chip', form.eligible_branches.includes(b) && 'active']"
            @click="toggleBranch(b)"
          >{{ b }}</span>
        </div>
      </div>
      <div class="form-group">
        <label>Skills required</label>
        <input v-model="form.skills_required" class="form-control" placeholder="Python, SQL, REST APIs" />
      </div>
      <div class="form-group">
        <label>Application deadline</label>
        <input v-model="form.application_deadline" type="date" class="form-control" />
      </div>
      <div style="display:flex;gap:8px">
        <button class="btn btn-primary" :disabled="saving" @click="submitDrive">
          {{ saving ? 'Submitting…' : 'Submit for admin approval' }}
        </button>
        <button class="btn" @click="showForm = false">Cancel</button>
      </div>
    </div>

    <!-- Drive list -->
    <div v-if="loading" class="spinner"></div>
    <div v-else-if="!drives.length && !showForm" class="empty-state card">
      <div class="icon">📋</div>
      <p>No drives yet. Create your first drive to start recruiting.</p>
    </div>
    <div v-else>
      <div
        v-for="d in drives" :key="d.id"
        class="drive-card"
        @click="$router.push(`/company/drives/${d.id}/applicants`)"
      >
        <div>
          <div style="font-weight:600;font-size:0.95rem">{{ d.title }}</div>
          <div style="color:var(--text2);font-size:0.82rem;margin-top:2px">{{ d.job_type }} · {{ d.location || 'Remote' }}</div>
          <div class="drive-meta">
            <span class="pill">₹{{ fmtSalary(d.salary_min) }} – ₹{{ fmtSalary(d.salary_max) }}</span>
            <span class="pill">CGPA ≥ {{ d.min_cgpa }}</span>
            <span class="pill">{{ d.interview_mode }}</span>
            <span class="pill" v-if="d.application_deadline">
              Deadline: {{ fmtDate(d.application_deadline) }}
            </span>
          </div>
          <div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap">
            <span v-for="br in d.eligible_branches" :key="br" class="pill">{{ br }}</span>
          </div>
        </div>
        <div class="drive-actions">
          <StatusBadge :status="d.status" />
          <span style="font-size:0.78rem;color:var(--text2)">{{ d.applications_count }} applicant(s)</span>
          <button class="btn btn-sm btn-primary" @click.stop="$router.push(`/company/drives/${d.id}/applicants`)">
            View applicants
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { companyAPI } from '@/services/api'
import { useToastStore } from '@/store/toast'
import StatusBadge from '@/components/common/StatusBadge.vue'

const toast    = useToastStore()
const drives   = ref([])
const loading  = ref(false)
const saving   = ref(false)
const showForm = ref(false)
const allBranches = ['CSE','ECE','IT','DS','ME','EEE','Civil','Chemical']

const form = reactive({
  title: '', job_description: '', job_type: 'Full-time',
  interview_mode: 'In-person', salary_min: '', salary_max: '',
  min_cgpa: '', location: '', eligible_branches: [],
  skills_required: '', application_deadline: '',
})

onMounted(fetch)

async function fetch() {
  loading.value = true
  try { const { data } = await companyAPI.getDrives(); drives.value = data }
  catch { toast.error('Failed to load drives') }
  finally { loading.value = false }
}

function toggleBranch(b) {
  const i = form.eligible_branches.indexOf(b)
  i >= 0 ? form.eligible_branches.splice(i, 1) : form.eligible_branches.push(b)
}

async function submitDrive() {
  if (!form.title) { toast.error('Job title is required'); return }
  saving.value = true
  try {
    await companyAPI.createDrive({
      ...form,
      salary_min: form.salary_min ? +form.salary_min : null,
      salary_max: form.salary_max ? +form.salary_max : null,
      min_cgpa:   form.min_cgpa   ? +form.min_cgpa   : null,
      eligible_years: [4],
      application_deadline: form.application_deadline
        ? new Date(form.application_deadline).toISOString() : null,
    })
    toast.success('Drive submitted for admin approval')
    showForm.value = false
    Object.assign(form, { title:'', job_description:'', salary_min:'', salary_max:'',
      min_cgpa:'', location:'', eligible_branches:[], skills_required:'', application_deadline:'' })
    fetch()
  } catch (e) {
    toast.error(e.response?.data?.error || 'Failed to create drive')
  } finally { saving.value = false }
}

function fmtSalary(v) {
  if (!v) return '—'
  return v >= 100000 ? (v/100000).toFixed(1)+'L' : v.toLocaleString()
}
function fmtDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-IN', { day:'numeric', month:'short', year:'numeric' })
}
</script>