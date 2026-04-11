<template>
  <div class="auth-page py-4">
    <div class="auth-card">
      <div class="auth-logo">Student <span>Register</span></div>
      <div class="card p-4">
        <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>

        <div class="row g-3">
          <div class="col-6">
            <label class="form-label">Full Name *</label>
            <input v-model="form.name" class="form-control" />
          </div>
          <div class="col-6">
            <label class="form-label">Roll Number</label>
            <input v-model="form.roll_number" class="form-control" />
          </div>
          <div class="col-12">
            <label class="form-label">Email *</label>
            <input v-model="form.email" type="email" class="form-control" />
          </div>
          <div class="col-12">
            <label class="form-label">Password *</label>
            <input v-model="form.password" type="password" class="form-control" />
          </div>
          <div class="col-4">
            <label class="form-label">Branch</label>
            <input v-model="form.branch" class="form-control" placeholder="CSE" />
          </div>
          <div class="col-4">
            <label class="form-label">Year</label>
            <input v-model.number="form.year" type="number" class="form-control" placeholder="3" />
          </div>
          <div class="col-4">
            <label class="form-label">CGPA</label>
            <input v-model.number="form.cgpa" type="number" step="0.1" class="form-control" placeholder="8.5" />
          </div>
          <div class="col-12">
            <label class="form-label">Phone</label>
            <input v-model="form.phone" class="form-control" />
          </div>
        </div>

        <button class="btn btn-success w-100 mt-4" :disabled="loading" @click="register">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          {{ loading ? 'Registering…' : 'Register' }}
        </button>

        <div class="text-center mt-3 small text-secondary">
          Already have an account? <RouterLink to="/login" class="text-success">Login</RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../main.js'

const router  = useRouter()
const error   = ref('')
const loading = ref(false)
const form    = reactive({ name:'', email:'', password:'', roll_number:'', branch:'', year:'', cgpa:'', phone:'' })

async function register() {
  error.value = ''
  if (!form.name || !form.email || !form.password) { error.value = 'Name, email and password are required'; return }
  loading.value = true
  try {
    const data = await api('/auth/register/student', { method: 'POST', body: JSON.stringify(form) })
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data.user))
    localStorage.setItem('profile', JSON.stringify(data.profile))
    router.push('/student/dashboard')
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>
