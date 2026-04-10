<template>
  <div class="page">
    <h2 style="margin-bottom:20px">Placement Drives</h2>
    <div class="search-bar">
      <select v-model="statusFilter" @change="load">
        <option value="all">All statuses</option>
        <option value="pending">Pending</option>
        <option value="approved">Approved</option>
        <option value="rejected">Rejected</option>
        <option value="closed">Closed</option>
      </select>
    </div>

    <div v-if="loading" class="spinner"></div>
    <div v-else-if="!drives.length" class="empty-state card">
      <div class="icon">📋</div><p>No drives found</p>
    </div>

    <div v-else class="table-wrap card" style="padding:0">
      <table>
        <thead>
          <tr><th>Title</th><th>Company</th><th>Deadline</th><th>Status</th><th>Actions</th></tr>
        </thead>
        <tbody>
          <tr v-for="d in drives" :key="d.id">
            <td>
              <div style="font-weight:600">{{ d.title }}</div>
              <small>{{ d.job_type }}</small>
            </td>
            <td>{{ d.company_name }}</td>
            <td>{{ fmtDate(d.application_deadline) }}</td>
            <td><span :class="statusBadge(d.status)">{{ d.status }}</span></td>
            <td>
              <div style="display:flex;gap:6px">
                <button v-if="d.status === 'pending'" class="btn btn-sm btn-success" @click="action(d.id,'approve')">Approve</button>
                <button v-if="d.status === 'pending'" class="btn btn-sm btn-danger"  @click="action(d.id,'reject')">Reject</button>
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
  } catch(e) { alert(e.message) }
  finally { loading.value = false }
}

async function action(id, type) {
  if (!confirm(`${type} this drive?`)) return
  try { await api(`/admin/drives/${id}/${type}`, { method: 'PATCH' }); load() }
  catch(e) { alert(e.message) }
}

function statusBadge(s) {
  return { pending:'badge badge-amber', approved:'badge badge-green', rejected:'badge badge-red', closed:'badge badge-gray' }[s] || 'badge badge-gray'
}
function fmtDate(d) { return d ? new Date(d).toLocaleDateString('en-IN', { day:'numeric', month:'short', year:'numeric' }) : '—' }
</script>
