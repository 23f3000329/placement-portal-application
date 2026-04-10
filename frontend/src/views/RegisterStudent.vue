<template>
  <div class="auth-page">
    <div class="auth-card card">
      <div class="auth-logo">Student <span>Register</span></div>
      <div v-if="error" class="error-msg">{{ error }}</div>

      <div class="form-grid-2">
        <div class="form-group">
          <label>Full Name *</label>
          <input v-model="form.name" class="form-control" />
        </div>
        <div class="form-group">
          <label>Roll Number</label>
          <input v-model="form.roll_number" class="form-control" />
        </div>
      </div>
      <div class="form-group">
        <label>Email *</label>
        <input v-model="form.email" type="email" class="form-control" />
      </div>
      <div class="form-group">
        <label>Password *</label>
        <input v-model="form.password" type="password" class="form-control" />
      </div>
      <div class="form-grid-3">
        <div class="form-group">
          <label>Branch</label>
          <input v-model="form.branch" class="form-control" placeholder="CSE" />
        </div>
        <div class="form-group">
          <label>Year</label>
          <input v-model.number="form.year" type="number" class="form-control" placeholder="3" />
        </div>
        <div class="form-group">
          <label>CGPA</label>
          <input v-model.number="form.cgpa" type="number" step="0.1" class="form-control" placeholder="8.5" />
        </div>
      </div>
      <div class="form-group">
        <label>Phone</label>
        <input v-model="form.phone" class="form-control" />
      </div>

      <button class="btn btn-primary btn-block" :disabled="loading" @click="register">
        {{ loading ? 'Registering…' : 'Register' }}
      </button>
      <div class="auth-footer">
        Already have an account? <RouterLink to="/login">Login</RouterLink>
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
const form = reactive({ name:'', email:'', password:'', roll_number:'', branch:'', year:'', cgpa:'', phone:'' })

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
