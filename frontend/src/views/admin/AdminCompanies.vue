<template>
  <div class="page">
    <h2 style="margin-bottom:20px">Companies</h2>

    <!-- Search & filter -->
    <div class="search-bar">
      <input v-model="query" placeholder="Search by name…" @input="load" />
      <select v-model="statusFilter" @change="load">
        <option value="all">All statuses</option>
        <option value="pending">Pending</option>
        <option value="approved">Approved</option>
        <option value="rejected">Rejected</option>
      </select>
    </div>

    <div v-if="loading" class="spinner"></div>

    <div v-else-if="!companies.length" class="empty-state card">
      <div class="icon">🏢</div><p>No companies found</p>
    </div>

    <div v-else class="table-wrap card" style="padding:0">
      <table>
        <thead>
          <tr>
            <th>Company</th><th>Industry</th><th>HR Contact</th>
            <th>Status</th><th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in companies" :key="c.id">
            <td>
              <div style="font-weight:600">{{ c.name }}</div>
              <small>{{ c.website }}</small>
            </td>
            <td>{{ c.industry || '—' }}</td>
            <td>{{ c.hr_contact || '—' }}</td>
            <td>
              <span :class="statusBadge(c.approval_status)">{{ c.approval_status }}</span>
              <span v-if="c.is_blacklisted" class="badge badge-red" style="margin-left:4px">blacklisted</span>
            </td>
            <td>
              <div style="display:flex;gap:6px;flex-wrap:wrap">
                <button v-if="c.approval_status === 'pending'"
                  class="btn btn-sm btn-success" @click="action(c.id,'approve')">Approve</button>
                <button v-if="c.approval_status === 'pending'"
                  class="btn btn-sm btn-danger"  @click="action(c.id,'reject')">Reject</button>
                <button v-if="!c.is_blacklisted && c.approval_status === 'approved'"
                  class="btn btn-sm btn-danger"  @click="action(c.id,'blacklist')">Blacklist</button>
                <button v-if="c.is_blacklisted"
                  class="btn btn-sm btn-success" @click="action(c.id,'activate')">Activate</button>
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
  } catch (e) {
    alert(e.message)
  } finally {
    loading.value = false
  }
}

async function action(id, type) {
  if (!confirm(`Are you sure you want to ${type} this company?`)) return
  try {
    await api(`/admin/companies/${id}/${type}`, { method: 'PATCH' })
    load()
  } catch (e) {
    alert(e.message)
  }
}

function statusBadge(s) {
  return { pending:'badge badge-amber', approved:'badge badge-green', rejected:'badge badge-red' }[s] || 'badge badge-gray'
}
</script>
