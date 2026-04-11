<template>
  <div class="page">
    <h4 class="mb-4 fw-semibold">Students</h4>

    <div class="row g-2 mb-3">
      <div class="col-md-5">
        <input v-model="query" class="form-control" placeholder="Search by name / roll / branch…" @input="load" />
      </div>
    </div>

    <div v-if="loading" class="spinner-center"><div class="spinner-border text-success"></div></div>

    <div v-else-if="!students.length" class="text-center text-secondary py-5">
      <i class="bi bi-people fs-1"></i><p class="mt-2">No students found</p>
    </div>

    <div v-else class="card p-0 overflow-hidden">
      <table class="table table-hover mb-0">
        <thead class="table-dark">
          <tr><th>Name</th><th>Roll No</th><th>Branch</th><th>CGPA</th><th>Year</th><th>Status</th><th>Actions</th></tr>
        </thead>
        <tbody>
          <tr v-for="s in students" :key="s.id">
            <td class="fw-semibold">{{ s.name }}</td>
            <td>{{ s.roll_number || '—' }}</td>
            <td>{{ s.branch || '—' }}</td>
            <td>{{ s.cgpa || '—' }}</td>
            <td>{{ s.year || '—' }}</td>
            <td>
              <span v-if="s.is_blacklisted" class="badge bg-danger">Blacklisted</span>
              <span v-else-if="s.is_placed"  class="badge bg-success">Placed</span>
              <span v-else                   class="badge bg-primary">Active</span>
            </td>
            <td>
              <button v-if="!s.is_blacklisted" class="btn btn-warning btn-sm" @click="action(s.id,'blacklist')">
                <i class="bi bi-slash-circle me-1"></i>Blacklist
              </button>
              <button v-else class="btn btn-success btn-sm" @click="action(s.id,'activate')">
                <i class="bi bi-arrow-counterclockwise me-1"></i>Activate
              </button>
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
  } catch (e) { alert(e.message) }
  finally { loading.value = false }
}

async function action(id, type) {
  if (!confirm(`${type} this student?`)) return
  try { await api(`/admin/students/${id}/${type}`, { method: 'PATCH' }); load() }
  catch (e) { alert(e.message) }
}
</script>
