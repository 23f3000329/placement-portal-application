<template>
  <div class="page">
    <h2 style="margin-bottom:20px">Dashboard</h2>

    <div class="stats-grid" v-if="stats">
      <div class="stat-card">
        <div class="stat-num" style="color:var(--blue)">{{ stats.total_drives }}</div>
        <div class="stat-label">Total Drives</div>
      </div>
      <div class="stat-card">
        <div class="stat-num" style="color:var(--green)">{{ stats.total_applicants }}</div>
        <div class="stat-label">Applicants</div>
      </div>
      <div class="stat-card">
        <div class="stat-num" style="color:var(--amber)">{{ stats.shortlisted }}</div>
        <div class="stat-label">Shortlisted</div>
      </div>
      <div class="stat-card">
        <div class="stat-num" style="color:#993556">{{ stats.selected }}</div>
        <div class="stat-label">Selected</div>
      </div>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
      <!-- Chart -->
      <div class="card">
        <div class="card-header"><span class="card-title">Application funnel</span></div>
        <canvas ref="funnelChart" style="max-height:220px"></canvas>
        <div v-if="!stats" class="empty-state" style="padding:20px">
          <div class="spinner"></div>
        </div>
      </div>

      <!-- Recent drives -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">Recent drives</span>
          <RouterLink to="/company/drives" class="btn btn-sm">View all →</RouterLink>
        </div>
        <div v-if="!drives.length" class="empty-state" style="padding:20px">
          <p>No drives yet</p>
        </div>
        <div v-for="d in drives.slice(0,4)" :key="d.id" style="padding:10px 0;border-bottom:1px solid var(--border)">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <div>
              <div style="font-weight:600;font-size:0.9rem">{{ d.title }}</div>
              <small>{{ d.applications_count }} applicants · {{ fmtDate(d.application_deadline) }}</small>
            </div>
            <StatusBadge :status="d.status" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { Chart, BarElement, CategoryScale, LinearScale, Tooltip, Legend, BarController } from 'chart.js'
import { companyAPI } from '@/services/api'
import { useToastStore } from '@/store/toast'
import StatusBadge from '@/components/common/StatusBadge.vue'

Chart.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend, BarController)

const toast       = useToastStore()
const stats       = ref(null)
const drives      = ref([])
const funnelChart = ref(null)

onMounted(async () => {
  try {
    const [sRes, dRes] = await Promise.all([companyAPI.getStats(), companyAPI.getDrives()])
    stats.value  = sRes.data
    drives.value = dRes.data
    await nextTick()
    buildChart()
  } catch { toast.error('Failed to load dashboard') }
})

function buildChart() {
  if (!funnelChart.value || !stats.value) return
  new Chart(funnelChart.value, {
    type: 'bar',
    data: {
      labels: ['Applicants', 'Shortlisted', 'Interview', 'Selected'],
      datasets: [{
        data: [
          stats.value.total_applicants,
          stats.value.shortlisted,
          stats.value.shortlisted,
          stats.value.selected,
        ],
        backgroundColor: ['#B5D4F4','#9FE1CB','#FAC775','#1D9E75'],
        borderRadius: 4,
      }]
    },
    options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } } }
  })
}

function fmtDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-IN', { day:'numeric', month:'short', year:'numeric' })
}
</script>