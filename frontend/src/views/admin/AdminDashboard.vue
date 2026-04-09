<template>
  <div class="page">
    <h2 style="margin-bottom:20px">Dashboard</h2>

    <!-- Stats -->
    <div class="stats-grid" v-if="stats">
      <div class="stat-card">
        <div class="stat-num" style="color:var(--green)">{{ stats.total_students }}</div>
        <div class="stat-label">Total Students</div>
      </div>
      <div class="stat-card">
        <div class="stat-num" style="color:var(--blue)">{{ stats.total_companies }}</div>
        <div class="stat-label">Approved Companies</div>
      </div>
      <div class="stat-card">
        <div class="stat-num" style="color:var(--amber)">{{ stats.active_drives }}</div>
        <div class="stat-label">Active Drives</div>
      </div>
      <div class="stat-card">
        <div class="stat-num" style="color:#993556">{{ stats.total_applications }}</div>
        <div class="stat-label">Total Applications</div>
      </div>
    </div>

    <!-- Pending banners -->
    <div v-if="stats?.pending_companies > 0" style="background:var(--amber-bg);border:1px solid #FAC775;border-radius:var(--radius);padding:12px 16px;margin-bottom:10px;font-size:0.88rem;color:var(--amber-text);display:flex;justify-content:space-between;align-items:center">
      <span>⚠ {{ stats.pending_companies }} company registration(s) awaiting approval</span>
      <RouterLink to="/admin/companies" class="btn btn-sm" style="background:var(--amber-bg);border-color:#FAC775;color:var(--amber-text)">Review →</RouterLink>
    </div>
    <div v-if="stats?.pending_drives > 0" style="background:var(--blue-bg);border:1px solid #B5D4F4;border-radius:var(--radius);padding:12px 16px;margin-bottom:20px;font-size:0.88rem;color:var(--blue-text);display:flex;justify-content:space-between;align-items:center">
      <span>ℹ {{ stats.pending_drives }} placement drive(s) awaiting approval</span>
      <RouterLink to="/admin/drives" class="btn btn-sm" style="background:var(--blue-bg);border-color:#B5D4F4;color:var(--blue-text)">Review →</RouterLink>
    </div>

    <!-- Charts row -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px">
      <!-- Application status doughnut -->
      <div class="card">
        <div class="card-header"><span class="card-title">Applications by status</span></div>
        <div style="max-width:260px;margin:0 auto">
          <canvas ref="statusChart"></canvas>
        </div>
      </div>

      <!-- Branch-wise bar -->
      <div class="card">
        <div class="card-header"><span class="card-title">Applications by branch</span></div>
        <canvas ref="branchChart" style="max-height:220px"></canvas>
      </div>
    </div>

    <!-- Drives by company bar -->
    <div class="card" style="margin-bottom:16px">
      <div class="card-header"><span class="card-title">Top companies by drives</span></div>
      <canvas ref="companyChart" style="max-height:180px"></canvas>
    </div>

    <!-- Placement rate card -->
    <div class="card">
      <div class="card-header">
        <span class="card-title">Placement overview</span>
        <span class="badge badge-teal">{{ stats?.placement_rate ?? 0 }}% placed</span>
      </div>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px">
        <div>
          <div style="font-size:0.75rem;color:var(--text2);margin-bottom:4px;font-weight:500;text-transform:uppercase;letter-spacing:.4px">Students placed</div>
          <div style="font-size:1.5rem;font-weight:600;color:var(--green)">{{ stats?.selected_students ?? 0 }}</div>
          <div class="progress-wrap" style="margin-top:8px">
            <div class="progress-bar" :style="`width:${stats?.placement_rate ?? 0}%;background:var(--green)`"></div>
          </div>
        </div>
        <div>
          <div style="font-size:0.75rem;color:var(--text2);margin-bottom:4px;font-weight:500;text-transform:uppercase;letter-spacing:.4px">Active drives</div>
          <div style="font-size:1.5rem;font-weight:600;color:var(--blue)">{{ stats?.active_drives ?? 0 }}</div>
        </div>
        <div>
          <div style="font-size:0.75rem;color:var(--text2);margin-bottom:4px;font-weight:500;text-transform:uppercase;letter-spacing:.4px">Pending approvals</div>
          <div style="font-size:1.5rem;font-weight:600;color:var(--amber)">{{ (stats?.pending_companies ?? 0) + (stats?.pending_drives ?? 0) }}</div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="spinner"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { Chart, ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend, DoughnutController, BarController } from 'chart.js'
import { adminAPI } from '@/services/api'
import { useToastStore } from '@/store/toast'

Chart.register(ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend, DoughnutController, BarController)

const toast       = useToastStore()
const stats       = ref(null)
const loading     = ref(false)
const statusChart  = ref(null)
const branchChart  = ref(null)
const companyChart = ref(null)

let charts = []

onMounted(async () => {
  loading.value = true
  try {
    const [sRes, cRes] = await Promise.all([adminAPI.getStats(), adminAPI.getCharts()])
    stats.value = sRes.data
    await nextTick()
    buildCharts(cRes.data)
  } catch {
    toast.error('Failed to load dashboard data')
  } finally {
    loading.value = false
  }
})

function buildCharts(data) {
  const statusColors = {
    applied:     '#B5D4F4',
    shortlisted: '#9FE1CB',
    interview:   '#FAC775',
    selected:    '#1D9E75',
    rejected:    '#F7C1C1',
  }
  const byStatus = data.by_status || {}
  const labels   = Object.keys(byStatus)
  const values   = Object.values(byStatus)

  if (statusChart.value && labels.length) {
    charts.push(new Chart(statusChart.value, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{ data: values, backgroundColor: labels.map(l => statusColors[l] || '#ddd'), borderWidth: 1 }]
      },
      options: { plugins: { legend: { position: 'bottom' } }, cutout: '60%' }
    }))
  }

  const branches = data.by_branch || []
  if (branchChart.value && branches.length) {
    charts.push(new Chart(branchChart.value, {
      type: 'bar',
      data: {
        labels: branches.map(b => b.branch),
        datasets: [{ label: 'Applications', data: branches.map(b => b.applications),
          backgroundColor: '#9FE1CB', borderRadius: 4 }]
      },
      options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } } }
    }))
  }

  const companies = data.by_company || []
  if (companyChart.value && companies.length) {
    charts.push(new Chart(companyChart.value, {
      type: 'bar',
      data: {
        labels: companies.map(c => c.company),
        datasets: [{ label: 'Drives', data: companies.map(c => c.drives),
          backgroundColor: '#B5D4F4', borderRadius: 4 }]
      },
      options: { indexAxis: 'y', plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true, ticks: { stepSize: 1 } } } }
    }))
  }
}
</script>