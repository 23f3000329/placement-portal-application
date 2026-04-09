<template>
  <div class="auth-page">
    <div class="auth-card card">
      <div class="auth-logo">Placement<span>Portal</span></div>
      <h2 style="text-align:center;margin-bottom:20px;font-weight:500;color:var(--text2)">Sign in</h2>

      <div v-if="error" class="error-msg">{{ error }}</div>

      <div class="form-group">
        <label>Email</label>
        <input v-model="form.email" type="email" class="form-control" placeholder="you@institute.edu" @keyup.enter="submit" />
      </div>
      <div class="form-group">
        <label>Password</label>
        <input v-model="form.password" type="password" class="form-control" placeholder="••••••••" @keyup.enter="submit" />
      </div>

      <button class="btn btn-primary btn-block" :disabled="loading" @click="submit" style="margin-top:4px">
        {{ loading ? 'Signing in…' : 'Sign in' }}
      </button>

      <div class="auth-footer">
        <p>Student? <RouterLink to="/register/student">Create account</RouterLink></p>
        <p style="margin-top:4px">Company? <RouterLink to="/register/company">Register company</RouterLink></p>
      </div>

      <div style="margin-top:20px;padding:12px;background:var(--bg);border-radius:var(--radius);font-size:0.78rem;color:var(--text2)">
        <b>Demo credentials</b><br>
        Admin: admin@institute.edu / admin@123<br>
        Company: hr@razorpay.com / company@123<br>
        Student: arjun@student.edu / student@123
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const auth   = useAuthStore()
const form   = reactive({ email: '', password: '' })
const error  = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  if (!form.email || !form.password) { error.value = 'Email and password required'; return }
  loading.value = true
  try {
    const data = await auth.login(form.email, form.password)
    const map = { admin: '/admin', company: '/company', student: '/student' }
    router.push(map[data.user.role] || '/')
  } catch (e) {
    error.value = e.response?.data?.error || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>