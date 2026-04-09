<template>
  <div class="page">
    <h2 style="margin-bottom:20px">Dashboard</h2>

    <!-- Stats -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-num" style="color:var(--blue)">{{ apps.length }}</div>
        <div class="stat-label">Applied</div>
      </div>
      <div class="stat-card">
        <div class="stat-num" style="color:var(--amber)">{{ countStatus('shortlisted') }}</div>
        <div class="stat-label">Shortlisted</div>
      </div>
      <div class="stat-card">
        <div class="stat-num" style="color:var(--blue)">{{ countStatus('interview') }}</div>
        <div class="stat-label">Interviews</div>
      </div>
      <div class="stat-card">
        <div class="stat-num" style="color:var(--green)">{{ countStatus('selected') }}</div>
        <div class="stat-label">Selected</div>
      </div>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
      <!-- Upcoming interviews -->
      <div class="card">
        <div class="card-header"><span class="card-title">Upcoming interviews</span></div>
        <div v-if="!upcomingInterviews.length" class="empty-state" style="padding:20px">
          <p>No interviews scheduled</p>
        </div>
        <div v-for="a in upcomingInterviews" :key="a.id" class="notif-item">
          <div class="notif-dot" style="background:var(--amber)"></div>
          <div>
            <div style="font-weight:600;font-size:0.88rem">{{ a.drive_title }}</div>
            <small>{{ a.company_name }} · {{ fmtDate(a.interview_date) }}</small>
          </div>
        </div>
      </div>

      <!-- Recent activity -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">Recent applications</span>
          <RouterLink to="/student/applications" class="btn btn-sm">View all →</RouterLink>
        </div>
        <div v-if="!apps.length" class="empty-state" style="padding:20px">
          <p>No applications yet</p>
          <RouterLink to="/student/drives" class="btn btn-sm btn-primary" style="margin-top:10px">Browse drives</RouterLink>
        </div>
        <div v-for="a in apps.slice(0,5)" :key="a.id" class="notif-item">
          <div class="notif-dot" :style="`background:${dotColor(a.status)}`"></div>
          <div style="flex:1">
            <div style="display:flex;justify-content:space-between;align-items:center">
              <div style="font-weight:600;font-size:0.88rem">{{ a.drive_title }}</div>
              <StatusBadge :status="a.status" />
            </div>
            <small>{{ a.company_name }} · {{ fmtDate(a.applied_at) }}</small>
          </div>
        </div>
      </div>
    </div>

    <!-- Eligible drives teaser -->
    <div class="card" style="margin-top:16px">
      <div class="card-header">
        <span class="card-title">Open drives you're eligible for</span>
        <RouterLink to="/student/drives" class="btn btn-sm btn-primary">Browse all →</RouterLink>
      </div>
      <div v-if="!eligibleDrives.length" class="empty-state" style="padding:20px">
        <p>No eligible drives found right now</p>
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px">
        <div v-for="d in eligibleDrives.slice(0,3)" :key="d.id"
          class="drive-card" style="margin:0"
          @click="$router.push(`/student/drives/${d.id}`)"
        >
          <div>
            <div style="font-weight:600;font-size:0.9rem">{{ d.title }}</div>
            <div style="color:var(--text2);font-size:0.8rem">{{ d.company_name }}</div>
            <div class="drive-meta">
              <span class="pill">{{ d.job_type }}</span>
              <span class="pill">CGPA ≥ {{ d.min_cgpa }}</span>
            </div>
          </div>
          <div class="drive-actions">
            <span class="badge badge-green">Eligible</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { studentAPI } from '@/services/api'
import { useToastStore } from '@/store/toast'
import StatusBadge from '@/components/common/StatusBadge.vue'

const toast = useToastStore()
const apps  = ref([])
const drives = ref([])

onMounted(async () => {
  try {
    const [aRes, dRes] = await Promise.all([studentAPI.getApplications(), studentAPI.getDrives()])
    apps.value   = aRes.data
    drives.value = dRes.data
  } catch { toast.error('Failed to load dashboard') }
})

const countStatus = s => apps.value.filter(a => a.status === s).length
const upcomingInterviews = computed(() =>
  apps.value.filter(a => a.interview_date && new Date(a.interview_date) >= new Date())
)
const eligibleDrives = computed(() =>
  drives.value.filter(d => d.is_eligible && !d.already_applied)
)

function dotColor(s) {
  return { applied:'var(--blue)', shortlisted:'var(--teal)', interview:'var(--amber)',
           selected:'var(--green)', rejected:'var(--red)' }[s] || 'var(--text3)'
}
function fmtDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('en-IN', { day:'numeric', month:'short', year:'numeric' })
}
</script>