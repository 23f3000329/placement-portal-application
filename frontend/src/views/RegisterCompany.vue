<template>
  <div class="auth-page">
    <div class="card" style="width:100%;max-width:500px;padding:28px">
      <div class="auth-logo">Placement<span>Portal</span></div>
      <h2 style="text-align:center;margin-bottom:6px;font-weight:500;color:var(--text2)">Company Registration</h2>
      <p style="text-align:center;color:var(--text3);font-size:0.85rem;margin-bottom:20px">Your account needs admin approval before you can log in.</p>

      <div v-if="success" style="background:var(--green-bg);color:var(--green-text);padding:12px;border-radius:var(--radius);margin-bottom:14px;font-size:0.88rem">
        ✓ Registration submitted! You'll be able to log in after admin approval.
        <RouterLink to="/login" style="display:block;margin-top:8px;font-weight:500">Back to login →</RouterLink>
      </div>

      <template v-if="!success">
        <div v-if="error" class="error-msg">{{ error }}</div>
        <div class="form-group">
          <label>Company name *</label>
          <input v-model="form.name" class="form-control" placeholder="Razorpay India Ltd" />
        </div>
        <div class="form-grid-2">
          <div class="form-group">
            <label>Email *</label>
            <input v-model="form.email" type="email" class="form-control" placeholder="hr@company.com" />
          </div>
          <div class="form-group">
            <label>Password *</label>
            <input v-model="form.password" type="password" class="form-control" placeholder="••••••••" />
          </div>
        </div>
        <div class="form-grid-2">
          <div class="form-group">
            <label>Industry</label>
            <select v-model="form.industry" class="form-control">
              <option value="">Select</option>
              <option v-for="i in industries" :key="i">{{ i }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Location</label>
            <input v-model="form.location" class="form-control" placeholder="Bangalore" />
          </div>
        </div>
        <div class="form-group">
          <label>Website</label>
          <input v-model="form.website" class="form-control" placeholder="https://company.com" />
        </div>
        <div class="form-grid-2">
          <div class="form-group">
            <label>HR contact name</label>
            <input v-model="form.hr_name" class="form-control" placeholder="Jane Smith" />
          </div>
          <div class="form-group">
            <label>HR phone</label>
            <input v-model="form.hr_contact" class="form-control" placeholder="9876543210" />
          </div>
        </div>
        <div class="form-group">
          <label>Company description</label>
          <textarea v-model="form.description" class="form-control" placeholder="Brief description of your company…"></textarea>
        </div>
        <button class="btn btn-primary btn-block" :disabled="loading" @click="submit">
          {{ loading ? 'Submitting…' : 'Submit for approval' }}
        </button>
        <div class="auth-footer">Already registered? <RouterLink to="/login">Sign in</RouterLink></div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useAuthStore } from '@/store/auth'

const auth    = useAuthStore()
const loading = ref(false)
const error   = ref('')
const success = ref(false)
const industries = ['Fintech','SaaS','IT Services','Payments','E-commerce','Healthcare','EdTech','Analytics','Consulting','Other']

const form = reactive({
  name: '', email: '', password: '', industry: '',
  location: '', website: '', hr_name: '', hr_contact: '', description: '',
})

async function submit() {
  error.value = ''
  if (!form.name || !form.email || !form.password) { error.value = 'Company name, email and password are required'; return }
  loading.value = true
  try {
    await auth.registerCompany(form)
    success.value = true
  } catch (e) {
    error.value = e.response?.data?.error || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>