<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-logo">Placement<span>Portal</span></div>

      <div class="card p-4">
        <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>

        <div class="mb-3">
          <label class="form-label">Email</label>
          <input v-model="email" type="email" class="form-control" placeholder="you@example.com" />
        </div>
        <div class="mb-3">
          <label class="form-label">Password</label>
          <input v-model="password" type="password" class="form-control" placeholder="••••••••"
            @keyup.enter="login" />
        </div>

        <button class="btn btn-success w-100" :disabled="loading" @click="login">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          {{ loading ? 'Logging in…' : 'Login' }}
        </button>

        <div class="text-center mt-3 small text-secondary">
          <RouterLink to="/register/student" class="text-success">Register as Student</RouterLink>
          &nbsp;·&nbsp;
          <RouterLink to="/register/company" class="text-success">Register as Company</RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../main.js'

const router   = useRouter()
const email    = ref('')
const password = ref('')
const error    = ref('')
const loading  = ref(false)

async function login() {
  error.value   = ''
  loading.value = true
  try {
    const data = await api('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email: email.value, password: password.value })
    })
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data.user))
    if (data.profile) localStorage.setItem('profile', JSON.stringify(data.profile))
    const map = { admin: '/admin', company: '/company', student: '/student' }
    router.push(map[data.user.role] || '/')
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>
