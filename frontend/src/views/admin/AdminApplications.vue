<template>
  <div class="page">
    <h2 style="margin-bottom:20px">All Applications</h2>

    <div class="search-bar">
      <input v-model="query" placeholder="Search student or drive…" />
      <select v-model="statusFilter">
        <option value="">All statuses</option>
        <option value="applied">Applied</option>
        <option value="shortlisted">Shortlisted</option>
        <option value="interview">Interview</option>
        <option value="selected">Selected</option>
        <option value="rejected">Rejected</option>
      </select>
    </div>

    <div v-if="loading" class="spinner"></div>

    <div v-else-if="!filtered.length" class="empty-state">
      <div class="icon">📄</div><p>No applications found</p>
    </div>

    <div v-else class="card" style="padding:0;overflow:hidden">
      <div style="padding:12px 16px;font-size:0.8rem;color:var(--text2);border-bottom:1px solid var(--border)">
        Showing {{ filtered.length }} application(s)
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Student</th>
              <th>Branch</th>
              <th>CGPA</th>
              <th>Drive</th>
              <th>Company</th>
              <th>Applied</th>
              <th>Interview</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in filtered" :key="a.id">
              <td>
                <div style="font-weight:600">{{ a.student_name }}</div>
                <small>{{ a.student_email }}</small>
              </td>
              <td>{{ a.student_branch || '—' }}</td>
              <td>{{ a.student_cgpa ?? '—' }}</td>
              <td>{{ a.drive_title }}</td>
              <td>{{ a.company_name }}</td>
              <td>{{ fmtDate(a.applied_at) }}</td>
              <td>{{ a.interview_date ? fmtDate(a.interview_date) : '—' }}</td>
              <td><StatusBadge :status="a.status" /></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { adminAPI } from '@/services/api'
import { useToastStore } from '@/store/toast'
import StatusBadge from '@/components/common/StatusBadge.vue'

const toast        = useToastStore()
const applications = ref([])
const loading      = ref(false)
const query        = ref('')
const statusFilter = ref('')

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await adminAPI.getApplications()
    applications.value = data
  } catch { toast.error('Failed to load applications') }
  finally { loading.value = false }
})

const filtered = computed(() => {
  let list = applications.value
  if (statusFilter.value) list = list.filter(a => a.status === statusFilter.value)
  if (query.value) {
    const q = query.value.toLowerCase()
    list = list.filter(a =>
      a.student_name?.toLowerCase().includes(q) ||
      a.drive_title?.toLowerCase().includes(q) ||
      a.company_name?.toLowerCase().includes(q)
    )
  }
  return list
})

function fmtDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-IN', { day:'numeric', month:'short', year:'numeric' })
}
</script>