<template>
  <div class="page">
    <h2 style="margin-bottom:20px">Placement Drives</h2>

    <div class="search-bar">
      <select v-model="statusFilter" @change="fetch">
        <option value="all">All statuses</option>
        <option value="pending">Pending</option>
        <option value="approved">Approved</option>
        <option value="rejected">Rejected</option>
        <option value="closed">Closed</option>
      </select>
    </div>

    <div v-if="loading" class="spinner"></div>

    <div v-else-if="!drives.length" class="empty-state">
      <div class="icon">📋</div><p>No drives found</p>
    </div>

    <div v-else class="card" style="padding:0;overflow:hidden">
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Drive</th>
              <th>Company</th>
              <th>Type</th>
              <th>Salary</th>
              <th>Min CGPA</th>
              <th>Deadline</th>
              <th>Applications</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="d in drives" :key="d.id">
              <td>
                <div style="font-weight:600">{{ d.title }}</div>
                <small>{{ d.location || '—' }}</small>
              </td>
              <td>{{ d.company_name }}</td>
              <td><span class="badge badge-gray">{{ d.job_type }}</span></td>
              <td>
                <span v-if="d.salary_min">
                  ₹{{ fmtSalary(d.salary_min) }}
                  <span v-if="d.salary_max"> – ₹{{ fmtSalary(d.salary_max) }}</span>
                </span>
                <span v-else>—</span>
              </td>
              <td>{{ d.min_cgpa || '—' }}</td>
              <td>{{ fmtDate(d.application_deadline) }}</td>
              <td>{{ d.applications_count }}</td>
              <td><StatusBadge :status="d.status" /></td>
              <td>
                <div style="display:flex;gap:6px">
                  <template v-if="d.status === 'pending'">
                    <button class="btn btn-sm btn-success" @click="action(d.id,'approve')">Approve</button>
                    <button class="btn btn-sm btn-danger"  @click="action(d.id,'reject')">Reject</button>
                  </template>
                  <template v-else-if="d.status === 'approved'">
                    <button class="btn btn-sm btn-danger" @click="action(d.id,'reject')">Close</button>
                  </template>
                  <template v-else-if="d.status === 'rejected'">
                    <button class="btn btn-sm btn-success" @click="action(d.id,'approve')">Re-approve</button>
                  </template>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminAPI } from '@/services/api'
import { useToastStore } from '@/store/toast'
import StatusBadge from '@/components/common/StatusBadge.vue'

const toast        = useToastStore()
const drives       = ref([])
const loading      = ref(false)
const statusFilter = ref('all')

onMounted(fetch)

async function fetch() {
  loading.value = true
  try {
    const { data } = await adminAPI.getDrives({ status: statusFilter.value })
    drives.value = data
  } catch { toast.error('Failed to load drives') }
  finally { loading.value = false }
}

async function action(id, type) {
  try {
    if (type === 'approve') await adminAPI.approveDrive(id)
    else await adminAPI.rejectDrive(id)
    toast.success(type === 'approve' ? 'Drive approved' : 'Drive rejected')
    fetch()
  } catch { toast.error('Action failed') }
}

function fmtSalary(v) {
  if (!v) return ''
  return v >= 100000 ? (v / 100000).toFixed(1) + 'L' : v.toLocaleString()
}
function fmtDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-IN', { day:'numeric', month:'short', year:'numeric' })
}
</script>