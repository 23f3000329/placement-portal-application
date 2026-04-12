<template>
  <div class="page">
    <h4 class="mb-4 fw-semibold">Browse Drives</h4>

    
    <div class="row g-2 mb-3">
      <div class="col-md-5">
        <input v-model="query" class="form-control" placeholder="Search by title, company, or skills…" />
      </div>
      <div class="col-md-3">
        <select v-model="typeFilter" class="form-select">
          <option value="">All types</option>
          <option value="Full-time">Full-time</option>
          <option value="Internship">Internship</option>
          <option value="Contract">Contract</option>
        </select>
      </div>
      <div class="col-md-3">
        <select v-model="eligFilter" class="form-select">
          <option value="">All drives</option>
          <option value="eligible">Eligible only</option>
          <option value="notapplied">Not applied yet</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="spinner-center">
      <div class="spinner-border text-success"></div>
    </div>

    <div v-else-if="!filtered.length" class="text-center text-secondary py-5">
      <i class="bi bi-briefcase fs-1"></i>
      <p class="mt-2">No drives match your search</p>
    </div>

    <template v-else>
      <p class="text-secondary small mb-3">{{ filtered.length }} drive(s) found</p>

      <div v-for="d in filtered" :key="d.id"
        :class="['drive-card', !d.is_eligible ? 'disabled' : '']"
        @click="d.is_eligible && $router.push(`/student/drives/${d.id}`)">
        <div>
          <div class="fw-semibold">{{ d.title }}</div>
          <div class="text-secondary small mt-1">{{ d.company_name }}</div>

          <div class="d-flex flex-wrap gap-1 mt-2">
            <span class="badge bg-secondary">{{ d.job_type }}</span>
            <span class="badge bg-secondary">{{ d.location || 'Remote' }}</span>
            <span v-if="d.salary_min" class="badge bg-secondary">
              ₹{{ fmtSalary(d.salary_min) }}{{ d.salary_max ? ' – ₹' + fmtSalary(d.salary_max) : '+' }}
            </span>
            <span class="badge bg-secondary">CGPA ≥ {{ d.min_cgpa }}</span>
            <span v-if="d.application_deadline"
              :class="['badge', isDeadlineSoon(d.application_deadline) ? 'bg-danger' : 'bg-secondary']">
              Closes {{ fmtDate(d.application_deadline) }}
            </span>
          </div>

          <div v-if="d.skills_required" class="text-secondary small mt-2">
            <i class="bi bi-tools me-1"></i>{{ d.skills_required }}
          </div>
        </div>

        <div class="drive-actions">
          <span v-if="d.already_applied"  class="badge bg-primary">Applied</span>
          <span v-else-if="d.is_eligible" class="badge bg-success">Eligible</span>
          <span v-else                    class="badge bg-danger">Not eligible</span>

          <button v-if="!d.already_applied && d.is_eligible"
            class="btn btn-success btn-sm mt-1"
            @click.stop="$router.push(`/student/drives/${d.id}`)">
            View &amp; Apply
          </button>
          <button v-else-if="d.already_applied"
            class="btn btn-outline-secondary btn-sm mt-1"
            @click.stop="$router.push(`/student/drives/${d.id}`)">
            View
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../../main.js'

const drives     = ref([])
const loading    = ref(false)
const query      = ref('')
const typeFilter = ref('')
const eligFilter = ref('')

onMounted(async () => {
  loading.value = true
  try { drives.value = await api('/student/drives') }
  catch (e) { alert('Failed to load drives: ' + e.message) }
  finally { loading.value = false }
})

const filtered = computed(() => {
  let list = drives.value
  if (typeFilter.value) list = list.filter(d => d.job_type === typeFilter.value)
  if (eligFilter.value === 'eligible')   list = list.filter(d => d.is_eligible)
  if (eligFilter.value === 'notapplied') list = list.filter(d => !d.already_applied)
  if (query.value) {
    const q = query.value.toLowerCase()
    list = list.filter(d =>
      d.title?.toLowerCase().includes(q) ||
      d.company_name?.toLowerCase().includes(q) ||
      d.skills_required?.toLowerCase().includes(q)
    )
  }
  return list
})

function isDeadlineSoon(d) { return d && (new Date(d) - new Date()) < 3 * 86400000 }
function fmtSalary(v) { return v >= 100000 ? (v / 100000).toFixed(1) + 'L' : v?.toLocaleString() }
function fmtDate(d) { return d ? new Date(d).toLocaleDateString('en-IN', { day:'numeric', month:'short', year:'numeric' }) : '' }
</script>
