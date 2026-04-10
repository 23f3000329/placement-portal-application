<template>
  <div class="page">
    <h2 style="margin-bottom:20px">Dashboard</h2>

    <div v-if="loading" class="spinner"></div>

    <template v-else>
      <!-- Stats cards -->
      <div class="stats-grid">
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

      <!-- Pending alerts -->
      <div v-if="stats.pending_companies > 0" class="alert-banner amber">
        ⚠ {{ stats.pending_companies }} company registration(s) awaiting approval
        <RouterLink to="/admin/companies" class="btn btn-sm">Review →</RouterLink>
      </div>
      <div v-if="stats.pending_drives > 0" class="alert-banner blue" style="margin-bottom:20px">
        ℹ {{ stats.pending_drives }} placement drive(s) awaiting approval
        <RouterLink to="/admin/drives" class="btn btn-sm">Review →</RouterLink>
      </div>

      <!-- Placement overview -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">Placement overview</span>
          <span class="badge badge-teal">{{ stats.placement_rate }}% placed</span>
        </div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px">
          <div>
            <div class="overview-label">Students placed</div>
            <div class="overview-num" style="color:var(--green)">{{ stats.selected_students }}</div>
            <div class="progress-wrap">
              <div class="progress-bar" :style="`width:${stats.placement_rate}%;background:var(--green)`"></div>
            </div>
          </div>
          <div>
            <div class="overview-label">Active drives</div>
            <div class="overview-num" style="color:var(--blue)">{{ stats.active_drives }}</div>
          </div>
          <div>
            <div class="overview-label">Pending approvals</div>
            <div class="overview-num" style="color:var(--amber)">{{ stats.pending_companies + stats.pending_drives }}</div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../../main.js'

const loading = ref(true)
const stats   = ref({
  total_students: 0, total_companies: 0, active_drives: 0,
  total_applications: 0, pending_companies: 0, pending_drives: 0,
  selected_students: 0, placement_rate: 0
})

onMounted(async () => {
  try {
    stats.value = await api('/admin/stats')
  } catch (e) {
    alert('Failed to load stats: ' + e.message)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.alert-banner {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px; border-radius: var(--radius); margin-bottom: 10px; font-size: 0.88rem;
}
.alert-banner.amber { background: var(--amber-bg); border: 1px solid #FAC775; color: var(--amber-text); }
.alert-banner.blue  { background: var(--blue-bg);  border: 1px solid #B5D4F4; color: var(--blue-text); }
.overview-label { font-size: 0.75rem; color: var(--text2); margin-bottom: 4px; font-weight: 500; text-transform: uppercase; letter-spacing: .4px; }
.overview-num   { font-size: 1.5rem; font-weight: 600; }
</style>
