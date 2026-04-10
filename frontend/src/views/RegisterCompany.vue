<template>
  <div class="auth-page">
    <div class="auth-card card" style="max-width:480px">
      <div class="auth-logo">Company <span>Register</span></div>
      <div v-if="error"   class="error-msg">{{ error }}</div>
      <div v-if="success" class="success-msg">{{ success }}</div>

      <template v-if="!success">
        <div class="form-grid-2">
          <div class="form-group">
            <label>Company Name *</label>
            <input v-model="form.name" class="form-control" />
          </div>
          <div class="form-group">
            <label>Industry</label>
            <input v-model="form.industry" class="form-control" placeholder="IT / Finance…" />
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
        <div class="form-grid-2">
          <div class="form-group">
            <label>HR Name</label>
            <input v-model="form.hr_name" class="form-control" />
          </div>
          <div class="form-group">
            <label>HR Contact</label>
            <input v-model="form.hr_contact" class="form-control" />
          </div>
        </div>
        <div class="form-group">
          <label>Website</label>
          <input v-model="form.website" class="form-control" placeholder="https://…" />
        </div>
        <div class="form-group">
          <label>Location</label>
          <input v-model="form.location" class="form-control" />
        </div>
        <div class="form-group">
          <label>Description</label>
          <textarea v-model="form.description" class="form-control" rows="3"></textarea>
        </div>
        <button class="btn btn-primary btn-block" :disabled="loading" @click="register">
          {{ loading ? 'Registering…' : 'Register Company' }}
        </button>
      </template>

      <div class="auth-footer">
        <RouterLink to="/login">Back to Login</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { api } from '../main.js'

const error   = ref('')
const success = ref('')
const loading = ref(false)
const form = reactive({ name:'', email:'', password:'', industry:'', hr_name:'', hr_contact:'', website:'', location:'', description:'' })

async function register() {
  error.value = ''
  if (!form.name || !form.email || !form.password) { error.value = 'Name, email and password are required'; return }
  loading.value = true
  try {
    await api('/auth/register/company', { method: 'POST', body: JSON.stringify(form) })
    success.value = 'Registration submitted! An admin will review and approve your account.'
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>
