<template>
  <div class="page">
    <h4 class="mb-4 fw-semibold">Dashboard</h4>

    <div v-if="loading" class="spinner-center"><div class="spinner-border text-success"></div></div>

    <template v-else>
      <!-- Stats -->
      <div class="row g-3 mb-4">
        <div class="col-sm-6 col-xl-3">
          <div class="card text-center p-3">
            <div class="stat-num text-primary">{{ apps.length }}</div>
            <div class="stat-label">Applied</div>
          </div>
        </div>
        <div class="col-sm-6 col-xl-3">
          <div class="card text-center p-3">
            <div class="stat-num text-warning">{{ countStatus('shortlisted') }}</div>
            <div class="stat-label">Shortlisted</div>
          </div>
        </div>
        <div class="col-sm-6 col-xl-3">
          <div class="card text-center p-3">
            <div class="stat-num text-info">{{ countStatus('interview') }}</div>
            <div class="stat-label">Interviews</div>
          </div>
        </div>
        <div class="col-sm-6 col-xl-3">
          <div class="card text-center p-3">
            <div class="stat-num text-success">{{ countStatus('selected') }}</div>
            <div class="stat-label">Selected</div>
          </div>
        </div>
      </div>

      <div class="row g-3 mb-3">
        <!-- Upcoming interviews -->
        <div class="col-md-6">
          <div class="card h-100">
            <div class="card-header fw-semibold">Upcoming interviews</div>
            <div v-if="!upcomingInterviews.length" class="card-body text-secondary text-center py-4">
              No interviews scheduled
            </div>
            <ul v-else class="list-group list-group-flush">
              <li v-for="a in upcomingInterviews" :key="a.id" class="list-group-item">
                <div class="d-flex align-items-start gap-2">
                  <span class="badge bg-warning mt-1">&nbsp;</span>
                  <div>
                    <div class="fw-semibold small">{{ a.drive_title }}</div>
                    <small class="text-secondary">{{ a.company_name }} · {{ fmtDate(a.interview_date) }}</small>
                  </div>
                </div>
              </li>
            </ul>
          </div>
        </div>

        <!-- Recent applications -->
        <div class="col-md-6">
          <div class="card h-100">
            <div class="card-header d-flex justify-content-between align-items-center">
              <span class="fw-semibold">Recent applications</span>
              <RouterLink to="/student/applications" class="btn btn-outline-success btn-sm">View all →</RouterLink>
            </div>
            <div v-if="!apps.length" class="card-body text-center text-secondary py-4">
              <p>No applications yet</p>
              <RouterLink to="/student/drives" class="btn btn-success btn-sm">Browse drives</RouterLink>
            </div>
            <ul v-else class="list-group list-group-flush">
              <li v-for="a in apps.slice(0,5)" :key="a.id" class="list-group-item">
                <div class="d-flex justify-content-between align-items-start">
                  <div>
                    <div class="fw-semibold small">{{ a.drive_title }}</div>
                    <small class="text-secondary">{{ a.company_name }} · {{ fmtDate(a.applied_at) }}</small>
                  </div>
                  <span :class="statusBadge(a.status)">{{ a.status }}</span>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Eligible drives teaser -->
      <div class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
          <span class="fw-semibold">Open drives you're eligible for</span>
          <RouterLink to="/student/drives" class="btn btn-success btn-sm">Browse all →</RouterLink>
        </div>
        <div v-if="!eligibleDrives.length" class="card-body text-center text-secondary py-4">
          No eligible drives found right now
        </div>
        <div v-else class="card-body">
          <div class="row g-3">
            <div v-for="d in eligibleDrives.slice(0,3)" :key="d.id" class="col-md-4">
              <div class="card h-100 border-success border-opacity-50" style="cursor:pointer"
                @click="$router.push(`/student/drives/${d.id}`)">
                <div class="card-body">
                  <div class="fw-semibold mb-1">{{ d.title }}</div>
                  <div class="text-secondary small mb-2">{{ d.company_name }}</div>
                  <span class="badge bg-secondary me-1">{{ d.job_type }}</span>
                  <span class="badge bg-secondary">CGPA ≥ {{ d.min_cgpa }}</span>
                </div>
                <div class="card-footer">
                  <span class="badge bg-success">Eligible</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../../main.js'

const loading = ref(true)
const apps    = ref([])
const drives  = ref([])

onMounted(async () => {
  try {
    const [appsData, drivesData] = await Promise.all([api('/student/applications'), api('/student/drives')])
    apps.value   = appsData
    drives.value = drivesData
  } catch (e) { alert('Failed to load dashboard: ' + e.message) }
  finally { loading.value = false }
})

function countStatus(s) { return apps.value.filter(a => a.status === s).length }
const eligibleDrives      = computed(() => drives.value.filter(d => d.is_eligible && !d.already_applied))
const upcomingInterviews  = computed(() => apps.value.filter(a => a.interview_date && new Date(a.interview_date) >= new Date()))

function statusBadge(s) {
  return { applied:'badge bg-primary', shortlisted:'badge bg-info text-dark', interview:'badge bg-warning text-dark', selected:'badge bg-success', rejected:'badge bg-danger' }[s] || 'badge bg-secondary'
}
function fmtDate(d) { return d ? new Date(d).toLocaleDateString('en-IN', { day:'numeric', month:'short', year:'numeric' }) : '' }
</script>
