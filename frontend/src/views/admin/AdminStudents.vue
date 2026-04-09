<template>
  <div class="page">
    <h2 style="margin-bottom:20px">Students</h2>

    <div class="search-bar">
      <input v-model="query" placeholder="Search by name or roll number…" @input="fetch" />
    </div>

    <div v-if="loading" class="spinner"></div>

    <div v-else-if="!students.length" class="empty-state">
      <div class="icon">🎓</div><p>No students found</p>
    </div>

    <div v-else class="card" style="padding:0;overflow:hidden">
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Student</th>
              <th>Branch</th>
              <th>CGPA</th>
              <th>Year</th>
              <th>Status</th>
              <th>Placed</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in students" :key="s.id">
              <td>
                <div style="display:flex;align-items:center;gap:10px">
                  <div class="avatar" :style="`background:${avatarBg(s.name)};color:${avatarText(s.name)}`">
                    {{ initials(s.name) }}
                  </div>
                  <div>
                    <div style="font-weight:600">{{ s.name }}</div>
                    <small>{{ s.email }}</small><br>
                    <small v-if="s.roll_number">{{ s.roll_number }}</small>
                  </div>
                </div>
              </td>
              <td>{{ s.branch || '—' }}</td>
              <td>{{ s.cgpa ?? '—' }}</td>
              <td>{{ s.year ? `Year ${s.year}` : '—' }}</td>
              <td>
                <StatusBadge :status="s.is_blacklisted ? 'blacklisted' : s.is_active ? 'active' : 'inactive'" />
              </td>
              <td>
                <span v-if="s.is_placed" class="badge badge-green">Placed</span>
                <span v-else class="badge badge-gray">—</span>
              </td>
              <td>
                <button v-if="!s.is_blacklisted" class="btn btn-sm btn-danger"
                  @click="action(s.id,'blacklist')">Blacklist</button>
                <button v-else class="btn btn-sm btn-success"
                  @click="action(s.id,'activate')">Restore</button>
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

const toast    = useToastStore()
const students = ref([])
const loading  = ref(false)
const query    = ref('')

const palette = [
  ['#E1F5EE','#085041'],['#E6F1FB','#0C447C'],['#FAEEDA','#633806'],
  ['#FCEBEB','#791F1F'],['#F1EFE8','#444441'],
]
function initials(n) { return n?.split(' ').map(w=>w[0]).join('').toUpperCase().slice(0,2) || '?' }
function avatarBg(n)   { return palette[(n?.charCodeAt(0) || 0) % palette.length][0] }
function avatarText(n) { return palette[(n?.charCodeAt(0) || 0) % palette.length][1] }

onMounted(fetch)

async function fetch() {
  loading.value = true
  try {
    const { data } = await adminAPI.getStudents({ q: query.value })
    students.value = data
  } catch { toast.error('Failed to load students') }
  finally { loading.value = false }
}

async function action(id, type) {
  try {
    if (type === 'blacklist') await adminAPI.blacklistStudent(id)
    else await adminAPI.activateStudent(id)
    toast.success(type === 'blacklist' ? 'Student blacklisted' : 'Student restored')
    fetch()
  } catch { toast.error('Action failed') }
}
</script>