<template>
  <div class="page">
    <h4 class="mb-4 fw-semibold">Companies</h4>

    
    <div class="row g-2 mb-3">
      <div class="col-md-6">
        <input v-model="query" class="form-control" placeholder="Search by name…" @input="load" />
      </div>
      <div class="col-md-3">
        <select v-model="statusFilter" class="form-select" @change="load">
          <option value="all">All statuses</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="spinner-center"><div class="spinner-border text-success"></div></div>

    <div v-else-if="!companies.length" class="text-center text-secondary py-5">
      <i class="bi bi-building fs-1"></i><p class="mt-2">No companies found</p>
    </div>

    <div v-else class="card p-0 overflow-hidden">
      <table class="table table-hover mb-0">
        <thead class="table-dark">
          <tr>
            <th>Company</th><th>Industry</th><th>HR Contact</th><th>Status</th><th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in companies" :key="c.id">
            <td>
              <div class="fw-semibold">{{ c.name }}</div>
              <small class="text-secondary">{{ c.website }}</small>
            </td>
            <td>{{ c.industry || '—' }}</td>
            <td>{{ c.hr_contact || '—' }}</td>
            <td>
              <span :class="statusBadge(c.approval_status)">{{ c.approval_status }}</span>
              <span v-if="c.is_blacklisted" class="badge bg-danger ms-1">blacklisted</span>
            </td>
            <td>
              <div class="d-flex gap-1 flex-wrap">
                <button v-if="c.approval_status === 'pending'"
                  class="btn btn-success btn-sm" @click="action(c.id,'approve')">
                  <i class="bi bi-check2"></i> Approve
                </button>
                <button v-if="c.approval_status === 'pending'"
                  class="btn btn-danger btn-sm" @click="action(c.id,'reject')">
                  <i class="bi bi-x"></i> Reject
                </button>
                <button v-if="!c.is_blacklisted && c.approval_status === 'approved'"
                  class="btn btn-warning btn-sm" @click="action(c.id,'blacklist')">
                  <i class="bi bi-slash-circle"></i> Blacklist
                </button>
                <button v-if="c.is_blacklisted"
                  class="btn btn-success btn-sm" @click="action(c.id,'activate')">
                  <i class="bi bi-arrow-counterclockwise"></i> Activate
                </button>
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

const companies    = ref([])
const loading      = ref(false)
const query        = ref('')
const statusFilter = ref('all')

onMounted(load)

async function load() {
  loading.value = true
  try {
    const params = new URLSearchParams({ q: query.value, status: statusFilter.value })
    companies.value = await api('/admin/companies?' + params)
  } catch (e) { alert(e.message) }
  finally { loading.value = false }
}

async function action(id, type) {
  if (!confirm(`${type} this company?`)) return
  loading.value=true
  try { await api(`/admin/companies/${id}/${type}`, { method: 'PATCH' }); await load() }
  catch (e) { alert(e.message) }
  finally{
    loading.value=false
  }
}

function statusBadge(s) {
  return { pending:'badge bg-warning text-dark', approved:'badge bg-success', rejected:'badge bg-danger' }[s] || 'badge bg-secondary'
}
</script>
