<template>
  <div class="page">
    <h4 class="mb-4 fw-semibold">Company Profile</h4>

    <div class="card" style="max-width:680px">
      <div class="card-body">
        <div v-if="loading" class="spinner-center"><div class="spinner-border text-success"></div></div>

        <template v-else>
          <div v-if="saved"  class="alert alert-success py-2">✓ Profile updated successfully</div>
          <div v-if="error"  class="alert alert-danger  py-2">{{ error }}</div>

          <div class="row g-3 mb-3">
            <div class="col-md-6">
              <label class="form-label">Company Name *</label>
              <input v-model="form.name" class="form-control" />
            </div>
            <div class="col-md-6">
              <label class="form-label">Industry</label>
              <select v-model="form.industry" class="form-select">
                <option value="">Select</option>
                <option v-for="i in industries" :key="i">{{ i }}</option>
              </select>
            </div>
            <div class="col-md-6">
              <label class="form-label">Website</label>
              <input v-model="form.website" class="form-control" placeholder="https://company.com" />
            </div>
            <div class="col-md-6">
              <label class="form-label">Location</label>
              <input v-model="form.location" class="form-control" placeholder="Bangalore" />
            </div>
            <div class="col-md-6">
              <label class="form-label">HR Name</label>
              <input v-model="form.hr_name" class="form-control" />
            </div>
            <div class="col-md-6">
              <label class="form-label">HR Contact</label>
              <input v-model="form.hr_contact" class="form-control" placeholder="9876543210" />
            </div>
            <div class="col-12">
              <label class="form-label">About Company</label>
              <textarea v-model="form.description" class="form-control" rows="4"
                placeholder="Describe your company, culture, and what you offer…"></textarea>
            </div>
          </div>

          <button class="btn btn-success" :disabled="saving" @click="save">
            <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
            {{ saving ? 'Saving…' : 'Save changes' }}
          </button>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { api } from '../../main.js'

const loading    = ref(true)
const saving     = ref(false)
const saved      = ref(false)
const error      = ref('')
const industries = ['Fintech','SaaS','IT Services','Payments','E-commerce','Healthcare','EdTech','Analytics','Consulting','Other']
const form       = reactive({ name:'', industry:'', website:'', location:'', hr_name:'', hr_contact:'', description:'' })

onMounted(async () => {
  try { Object.assign(form, await api('/company/profile')) }
  catch (e) { error.value = 'Failed to load profile: ' + e.message }
  finally { loading.value = false }
})

async function save() {
  error.value = ''
  if (!form.name) { error.value = 'Company name is required'; return }
  saving.value = true
  try {
    const updated = await api('/company/profile', { method:'PUT', body: JSON.stringify(form) })
    Object.assign(form, updated)
    localStorage.setItem('profile', JSON.stringify(updated))
    saved.value = true
    setTimeout(() => { saved.value = false }, 3000)
  } catch (e) { error.value = e.message }
  finally { saving.value = false }
}
</script>
