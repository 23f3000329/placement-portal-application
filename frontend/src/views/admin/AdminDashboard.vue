<template>
  <div class="page">
    <h4 class="mb-4 fw-semibold">Dashboard</h4>

    <div v-if="loading" class="spinner-center">
      <div class="spinner-border text-success"></div>
    </div>

    <template v-else>
      <div class="row g-3 mb-4">
        <div class="col-sm-6 col-xl-3">
          <div class="card text-center p-3">
            <div class="stat-num text-success">{{ stats.total_students }}</div>
            <div class="stat-label">Total Students</div>
          </div>
        </div>
        <div class="col-sm-6 col-xl-3">
          <div class="card text-center p-3">
            <div class="stat-num text-primary">{{ stats.total_companies }}</div>
            <div class="stat-label">Approved Companies</div>
          </div>
        </div>
        <div class="col-sm-6 col-xl-3">
          <div class="card text-center p-3">
            <div class="stat-num text-warning">{{ stats.active_drives }}</div>
            <div class="stat-label">Active Drives</div>
          </div>
        </div>
        <div class="col-sm-6 col-xl-3">
          <div class="card text-center p-3">
            <div class="stat-num text-info">{{ stats.total_applications }}</div>
            <div class="stat-label">Total Applications</div>
          </div>
        </div>
      </div>

      <!-- Pending alerts -->
      <div v-if="stats.pending_companies > 0" class="alert alert-warning d-flex justify-content-between align-items-center">
        <span><i class="bi bi-exclamation-triangle me-2"></i>{{ stats.pending_companies }} company registration(s) awaiting approval</span>
        <RouterLink to="/admin/companies" class="btn btn-warning btn-sm">Review →</RouterLink>
      </div>
      <div v-if="stats.pending_drives > 0" class="alert alert-info d-flex justify-content-between align-items-center">
        <span><i class="bi bi-info-circle me-2"></i>{{ stats.pending_drives }} placement drive(s) awaiting approval</span>
        <RouterLink to="/admin/drives" class="btn btn-info btn-sm">Review →</RouterLink>
      </div>

      <!-- Placement overview -->
      <div class="card p-4">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h6 class="mb-0 fw-semibold">Placement overview</h6>
          <span class="badge bg-success">{{ stats.placement_rate }}% placed</span>
        </div>
        <div class="row g-3">
          <div class="col-md-4">
            <div class="section-label">Students placed</div>
            <div class="fs-4 fw-bold text-success">{{ stats.selected_students }}</div>
            <div class="progress progress-thin mt-2">
              <div class="progress-bar bg-success" :style="`width:${stats.placement_rate}%`"></div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="section-label">Active drives</div>
            <div class="fs-4 fw-bold text-primary">{{ stats.active_drives }}</div>
          </div>
          <div class="col-md-4">
            <div class="section-label">Pending approvals</div>
            <div class="fs-4 fw-bold text-warning">{{ stats.pending_companies + stats.pending_drives }}</div>
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
const stats   = ref({ total_students:0, total_companies:0, active_drives:0, total_applications:0,
                       pending_companies:0, pending_drives:0, selected_students:0, placement_rate:0 })

onMounted(async () => {
  try { stats.value = await api('/admin/stats') }
  catch (e) { alert('Failed to load stats: ' + e.message) }
  finally { loading.value = false }
})
</script>
