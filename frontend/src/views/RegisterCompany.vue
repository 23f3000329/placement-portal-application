<template>
  <div class="auth-page py-4">
    <div style="width:100%;max-width:500px">
      <div class="auth-logo">Company <span>Register</span></div>
      <div class="card p-4">
        <div v-if="error"   class="alert alert-danger  py-2">{{ error }}</div>
        <div v-if="success" class="alert alert-success py-2">{{ success }}</div>

        <template v-if="!success">
          <div class="row g-3">
            <div class="col-6">
              <label class="form-label">Company Name *</label>
              <input v-model="form.name" class="form-control" />
            </div>
            <div class="col-6">
              <label class="form-label">Industry</label>
              <input v-model="form.industry" class="form-control" placeholder="IT / Finance…" />
            </div>
            <div class="col-12">
              <label class="form-label">Email *</label>
              <input v-model="form.email" type="email" class="form-control" />
            </div>
            <div class="col-12">
              <label class="form-label">Password *</label>
              <input v-model="form.password" type="password" class="form-control" />
            </div>
            <div class="col-6">
              <label class="form-label">HR Name</label>
              <input v-model="form.hr_name" class="form-control" />
            </div>
            <div class="col-6">
              <label class="form-label">HR Contact</label>
              <input v-model="form.hr_contact" class="form-control" />
            </div>
            <div class="col-12">
              <label class="form-label">Website</label>
              <input v-model="form.website" class="form-control" placeholder="https://…" />
            </div>
            <div class="col-12">
              <label class="form-label">Location</label>
              <input v-model="form.location" class="form-control" />
            </div>
            <div class="col-12">
              <label class="form-label">Description</label>
              <textarea v-model="form.description" class="form-control" rows="3"></textarea>
            </div>
          </div>

          <button class="btn btn-success w-100 mt-4" :disabled="loading" @click="register">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            {{ loading ? 'Registering…' : 'Register Company' }}
          </button>
        </template>

        <div class="text-center mt-3 small text-secondary">
          <RouterLink to="/login" class="text-success">Back to Login</RouterLink>
        </div>
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
const form    = reactive({ name:'', email:'', password:'', industry:'', hr_name:'', hr_contact:'', website:'', location:'', description:'' })

async function register() {
  error.value = ''
  if (!form.name || !form.email || !form.password) { error.value = 'Name, email and password are required'; return }
  loading.value = true
  try {
    await api('/auth/register/company', { method: 'POST', body: JSON.stringify(form) })
    success.value = 'Registration submitted! Admin will review and approve your account. You can then login.'
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>
