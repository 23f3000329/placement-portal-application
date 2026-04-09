<template>
  <div class="auth-page">
    <div class="card" style="width:100%;max-width:500px;padding:28px">
      <div class="auth-logo">Placement<span>Portal</span></div>
      <h2 style="text-align:center;margin-bottom:20px;font-weight:500;color:var(--text2)">Student Registration</h2>

      <div v-if="error" class="error-msg">{{ error }}</div>

      <div class="form-grid-2">
        <div class="form-group">
          <label>Full name *</label>
          <input v-model="form.name" class="form-control" placeholder="Arjun Menon" />
        </div>
        <div class="form-group">
          <label>Roll number</label>
          <input v-model="form.roll_number" class="form-control" placeholder="CS21001" />
        </div>
      </div>
      <div class="form-group">
        <label>Email *</label>
        <input v-model="form.email" type="email" class="form-control" placeholder="you@student.edu" />
      </div>
      <div class="form-group">
        <label>Password *</label>
        <input v-model="form.password" type="password" class="form-control" placeholder="Min. 6 characters" />
      </div>
      <div class="form-grid-3">
        <div class="form-group">
          <label>Branch</label>
          <select v-model="form.branch" class="form-control">
            <option value="">Select</option>
            <option v-for="b in branches" :key="b">{{ b }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>Year</label>
          <select v-model="form.year" class="form-control">
            <option value="">Select</option>
            <option v-for="y in [1,2,3,4]" :key="y">{{ y }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>CGPA</label>
          <input v-model="form.cgpa" type="number" step="0.1" min="0" max="10" class="form-control" placeholder="8.5" />
        </div>
      </div>
      <div class="form-group">
        <label>Phone</label>
        <input v-model="form.phone" class="form-control" placeholder="9876543210" />
      </div>

      <button class="btn btn-primary btn-block" :disabled="loading" @click="submit">
        {{ loading ? 'Creating account…' : 'Create account' }}
      </button>
      <div class="auth-footer">Already have an account? <RouterLink to="/login">Sign in</RouterLink></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const router  = useRouter()
const auth    = useAuthStore()
const loading = ref(false)
const error   = ref('')
const branches = ['CSE','ECE','IT','DS','ME','EEE','Civil','Chemical']

const form = reactive({
  name: '', roll_number: '', email: '', password: '',
  branch: '', year: '', cgpa: '', phone: '',
})

async function submit() {
  error.value = ''
  if (!form.name || !form.email || !form.password) { error.value = 'Name, email and password are required'; return }
  if (form.password.length < 6) { error.value = 'Password must be at least 6 characters'; return }
  loading.value = true
  try {
    await auth.registerStudent({ ...form, year: form.year ? +form.year : null, cgpa: form.cgpa ? +form.cgpa : null })
    router.push('/student/dashboard')
  } catch (e) {
    error.value = e.response?.data?.error || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>