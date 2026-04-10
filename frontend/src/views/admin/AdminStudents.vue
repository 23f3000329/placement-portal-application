<template>
  <div class="page">
    <h2 style="margin-bottom:20px">Students</h2>
    <div class="search-bar">
      <input v-model="query" placeholder="Search by name / roll / branch…" @input="load" />
    </div>

    <div v-if="loading" class="spinner"></div>

    <div v-else-if="!students.length" class="empty-state card">
      <div class="icon">🎓</div><p>No students found</p>
    </div>

    <div v-else class="table-wrap card" style="padding:0">
      <table>
        <thead>
          <tr><th>Name</th><th>Roll No</th><th>Branch</th><th>CGPA</th><th>Year</th><th>Status</th><th>Actions</th></tr>
        </thead>
        <tbody>
          <tr v-for="s in students" :key="s.id">
            <td>{{ s.name }}</td>
            <td>{{ s.roll_number || '—' }}</td>
            <td>{{ s.branch || '—' }}</td>
            <td>{{ s.cgpa || '—' }}</td>
            <td>{{ s.year || '—' }}</td>
            <td>
              <span v-if="s.is_blacklisted" class="badge badge-red">Blacklisted</span>
              <span v-else-if="s.is_placed"   class="badge badge-green">Placed</span>
              <span v-else                     class="badge badge-blue">Active</span>
            </td>
            <td>
              <button v-if="!s.is_blacklisted" class="btn btn-sm btn-danger"  @click="action(s.id,'blacklist')">Blacklist</button>
              <button v-else                    class="btn btn-sm btn-success" @click="action(s.id,'activate')">Activate</button>
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

const students = ref([])
const loading  = ref(false)
const query    = ref('')

onMounted(load)

async function load() {
  loading.value = true
  try {
    const params = new URLSearchParams({ q: query.value })
    students.value = await api('/admin/students?' + params)
  } catch(e) { alert(e.message) }
  finally { loading.value = false }
}

async function action(id, type) {
  if (!confirm(`${type} this student?`)) return
  try { await api(`/admin/students/${id}/${type}`, { method: 'PATCH' }); load() }
  catch(e) { alert(e.message) }
}
</script>
