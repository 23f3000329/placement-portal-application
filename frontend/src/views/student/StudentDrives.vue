<template>
  <div class="page">
    <h2 style="margin-bottom:20px">Browse Drives</h2>

    <div class="search-bar">
      <input v-model="query" placeholder="Search by title or skills…" />
      <select v-model="typeFilter">
        <option value="">All types</option>
        <option value="Full-time">Full-time</option>
        <option value="Internship">Internship</option>
        <option value="Contract">Contract</option>
      </select>
      <select v-model="eligFilter">
        <option value="">All drives</option>
        <option value="eligible">Eligible only</option>
        <option value="notapplied">Not applied</option>
      </select>
    </div>

    <div v-if="loading" class="spinner"></div>

    <div v-else-if="!filtered.length" class="empty-state card">
      <div class="icon">📋</div>
      <p>No drives match your search</p>
    </div>

    <div v-else>
      <div style="font-size:0.8rem;color:var(--text2);margin-bottom:12px">
        {{ filtered.length }} drive(s) found
      </div>
      <div
        v-for="d in filtered" :key="d.id"
        :class="['drive-card', !d.is_eligible && 'disabled']"
        @click="d.is_eligible && $router.push(`/student/drives/${d.id}`)"
      >
        <div>
          <div style="font-weight:600;font-size:0.95rem">{{ d.title }}</div>
          <div style="color:var(--text2);font-size:0.82rem;margin-top:2px">
            {{ d.company_name }} · {{ d.company_industry }}
          </div>
          <div class="drive-meta">
            <span class="pill">{{ d.job_type }}</span>
            <span class="pill">{{ d.location || 'Remote' }}</span>
            <span v-if="d.salary_min" class="pill">
              ₹{{ fmtSalary(d.salary_min) }}{{ d.salary_max ? ' – ₹' + fmtSalary(d.salary_max) : '+' }}
            </span>
            <span class="pill">CGPA ≥ {{ d.min_cgpa }}</span>
            <span v-if="d.application_deadline"
              :class="['pill', isDeadlineSoon(d.application_deadline) && 'pill-warn']"
              :style="isDeadlineSoon(d.application_deadline) ? 'color:var(--red-text);border-color:#F7C1C1' : ''"
            >
              Closes {{ fmtDate(d.application_deadline) }}
            </span>
          </div>
          <div style="margin-top:6px;display:flex;gap:4px;flex-wrap:wrap">
            <span v-for="b in d.eligible_branches" :key="b" class="pill">{{ b }}</span>
          </div>
          <div v-if="d.skills_required" style="margin-top:6px;font-size:0.78rem;color:var(--text2)">
            🛠 {{ d.skills_required }}
          </div>
        </div>
        <div class="drive-actions">
          <span v-if="d.already_applied" class="badge badge-blue">Applied</span>
          <span v-else-if="d.is_eligible"  class="badge badge-green">Eligible</span>
          <span v-else                      class="badge badge-red">Not eligible</span>
          <button
            v-if="!d.already_applied && d.is_eligible"
            class="btn btn-sm btn-primary"
            @click.stop="$router.push(`/student/drives/${d.id}`)"
          >View & Apply</button>
          <button v-else-if="d.already_applied" class="btn btn-sm"
            @click.stop="$router.push(`/student/drives/${d.id}`)">View</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { studentAPI } from '@/services/api'
import { useToastStore } from '@/store/toast'

const toast      = useToastStore()
const drives     = ref([])
const loading    = ref(false)
const query      = ref('')
const typeFilter = ref('')
const eligFilter = ref('')

onMounted(fetch)

async function fetch() {
  loading.value = true
  try { const { data } = await studentAPI.getDrives(); drives.value = data }
  catch { toast.error('Failed to load drives') }
  finally { loading.value = false }
}

const filtered = computed(() => {
  let list = drives.value
  if (typeFilter.value) list = list.filter(d => d.job_type === typeFilter.value)
  if (eligFilter.value === 'eligible')  list = list.filter(d => d.is_eligible)
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

function isDeadlineSoon(d) {
  return d && (new Date(d) - new Date()) < 3 * 86400000
}
function fmtSalary(v) {
  if (!v) return ''
  return v >= 100000 ? (v/100000).toFixed(1)+'L' : v.toLocaleString()
}
function fmtDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('en-IN', { day:'numeric', month:'short', year:'numeric' })
}
</script>