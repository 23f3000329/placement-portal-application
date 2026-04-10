<template>
  <div class="page">
    <h2 style="margin-bottom:20px">All Applications</h2>
    <div v-if="loading" class="spinner"></div>
    <div v-else-if="!applications.length" class="empty-state card">
      <div class="icon">📝</div><p>No applications yet</p>
    </div>
    <div v-else class="table-wrap card" style="padding:0">
      <table>
        <thead>
          <tr><th>Student</th><th>Drive</th><th>Company</th><th>Date</th><th>Status</th></tr>
        </thead>
        <tbody>
          <tr v-for="a in applications" :key="a.id">
            <td>{{ a.student_name }}</td>
            <td>{{ a.drive_title }}</td>
            <td>{{ a.company_name }}</td>
            <td>{{ fmtDate(a.applied_at) }}</td>
            <td><span :class="statusBadge(a.status)">{{ a.status }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../../main.js'

const applications = ref([])
const loading      = ref(false)

onMounted(async () => {
  loading.value = true
  try { applications.value = await api('/admin/applications') }
  catch(e) { alert(e.message) }
  finally { loading.value = false }
})

function statusBadge(s) {
  return { applied:'badge badge-blue', shortlisted:'badge badge-teal', interview:'badge badge-amber', selected:'badge badge-green', rejected:'badge badge-red' }[s] || 'badge badge-gray'
}
function fmtDate(d) { return d ? new Date(d).toLocaleDateString('en-IN', { day:'numeric', month:'short', year:'numeric' }) : '—' }
</script>
