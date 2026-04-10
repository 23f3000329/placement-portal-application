<template>
  <div class="auth-page">
    <div class="auth-card card">
      <div class="auth-logo">Placement<span>Portal</span></div>
      <div v-if="error" class="error-msg">{{ error }}</div>
      <div class="form-group">
        <label>Email</label>
        <input v-model="email" type="email" class="form-control" placeholder="you@example.com" />
      </div>
      <div class="form-group">
        <label>Password</label>
        <input v-model="password" type="password" class="form-control" placeholder="••••••••" />
      </div>
      <button class="btn btn-primary btn-block" :disabled="loading" @click="login">
        {{ loading ? 'Logging in…' : 'Login' }}
      </button>
      <div class="auth-footer">
        <RouterLink to="/register/student">Register as Student</RouterLink>
        &nbsp;·&nbsp;
        <RouterLink to="/register/company">Register as Company</RouterLink>
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
