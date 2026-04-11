<template>
  <div class="page">
    <h4 class="mb-4 fw-semibold">Placement Drives</h4>

    <div class="row g-2 mb-3">
      <div class="col-md-3">
        <select v-model="statusFilter" class="form-select" @change="load">
          <option value="all">All statuses</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
          <option value="closed">Closed</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="spinner-center"><div class="spinner-border text-success"></div></div>

    <div v-else-if="!drives.length" class="text-center text-secondary py-5">
      <i class="bi bi-briefcase fs-1"></i><p class="mt-2">No drives found</p>
    </div>

    <div v-else class="card p-0 overflow-hidden">
      <table class="table table-hover mb-0">
        <thead class="table-dark">
          <tr><th>Title</th><th>Company</th><th>Deadline</th><th>Status</th><th>Actions</th></tr>
        </thead>
        <tbody>
          <tr v-for="d in drives" :key="d.id">
            <td>
              <div class="fw-semibold">{{ d.title }}</div>
              <small class="text-secondary">{{ d.job_type }}</small>
            </td>
            <td>{{ d.company_name }}</td>
            <td>{{ fmtDate(d.application_deadline) }}</td>
            <td><span :class="statusBadge(d.status)">{{ d.status }}</span></td>
            <td>
              <div class="d-flex gap-1">
                <button v-if="d.status === 'pending'" class="btn btn-success btn-sm" @click="action(d.id,'approve')">
                  <i class="bi bi-check2"></i> Approve
                </button>
                <button v-if="d.status === 'pending'" class="btn btn-danger btn-sm" @click="action(d.id,'reject')">
                  <i class="bi bi-x"></i> Reject
                </button>
                <span v-if="d.status !== 'pending'" class="text-secondary small">No action needed</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../../main.js'

const drives       = ref([])
const loading      = ref(false)
const statusFilter = ref('all')

onMounted(load)

async function load() {
  loading.value = true
  try {
    const params = new URLSearchParams({ status: statusFilter.value })
    drives.value = await api('/admin/drives?' + params)
  } catch (e) { alert(e.message) }
  finally { loading.value = false }
}

async function action(id, type) {
  if (!confirm(`${type} this drive?`)) return
  try { await api(`/admin/drives/${id}/${type}`, { method: 'PATCH' }); load() }
  catch (e) { alert(e.message) }
}

function statusBadge(s) {
  return { pending:'badge bg-warning text-dark', approved:'badge bg-success', rejected:'badge bg-danger', closed:'badge bg-secondary' }[s] || 'badge bg-secondary'
}
function fmtDate(d) { return d ? new Date(d).toLocaleDateString('en-IN', { day:'numeric', month:'short', year:'numeric' }) : '—' }
</script>
