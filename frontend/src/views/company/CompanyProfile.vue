<template>
  <div class="page">
    <h2 style="margin-bottom:20px">Company Profile</h2>

    <div class="card" style="max-width:680px">
      <div style="display:flex;align-items:center;gap:14px;margin-bottom:24px;padding-bottom:20px;border-bottom:1px solid var(--border)">
        <div class="avatar avatar-lg" style="background:var(--blue-bg);color:var(--blue-text)">
          {{ initials(form.name) }}
        </div>
        <div>
          <div style="font-size:1.1rem;font-weight:600">{{ form.name || '—' }}</div>
          <div style="color:var(--text2);font-size:0.85rem">{{ auth.user?.email }}</div>
          <StatusBadge status="approved" style="margin-top:4px" />
        </div>
      </div>

      <div v-if="saved" style="background:var(--green-bg);color:var(--green-text);padding:10px 12px;border-radius:var(--radius);margin-bottom:14px;font-size:0.88rem">
        ✓ Profile updated successfully
      </div>

      <div class="form-grid-2">
        <div class="form-group">
          <label>Company name *</label>
          <input v-model="form.name" class="form-control" />
        </div>
        <div class="form-group">
          <label>Industry</label>
          <select v-model="form.industry" class="form-control">
            <option value="">Select</option>
            <option v-for="i in industries" :key="i">{{ i }}</option>
          </select>
        </div>
      </div>
      <div class="form-grid-2">
        <div class="form-group">
          <label>Website</label>
          <input v-model="form.website" class="form-control" placeholder="https://company.com" />
        </div>
        <div class="form-group">
          <label>Location</label>
          <input v-model="form.location" class="form-control" placeholder="Bangalore" />
        </div>
      </div>
      <div class="form-grid-2">
        <div class="form-group">
          <label>HR name</label>
          <input v-model="form.hr_name" class="form-control" />
        </div>
        <div class="form-group">
          <label>HR contact</label>
          <input v-model="form.hr_contact" class="form-control" placeholder="9876543210" />
        </div>
      </div>
      <div class="form-group">
        <label>About company</label>
        <textarea v-model="form.description" class="form-control" rows="4" placeholder="Describe your company, culture, and what you offer…"></textarea>
      </div>

      <button class="btn btn-primary" :disabled="saving" @click="save">
        {{ saving ? 'Saving…' : 'Save changes' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { companyAPI } from '@/services/api'
import { useAuthStore } from '@/store/auth'
import { useToastStore } from '@/store/toast'
import StatusBadge from '@/components/common/StatusBadge.vue'

const auth   = useAuthStore()
const toast  = useToastStore()
const saving = ref(false)
const saved  = ref(false)
const industries = ['Fintech','SaaS','IT Services','Payments','E-commerce','Healthcare','EdTech','Analytics','Consulting','Other']

const form = reactive({
  name:'', industry:'', website:'', location:'', hr_name:'', hr_contact:'', description:''
})

onMounted(async () => {
  try {
    const { data } = await companyAPI.getProfile()
    Object.assign(form, data)
  } catch { toast.error('Failed to load profile') }
})

function initials(n) { return n?.split(' ').map(w=>w[0]).join('').toUpperCase().slice(0,2) || 'CO' }

async function save() {
  if (!form.name) { toast.error('Company name is required'); return }
  saving.value = true
  try {
    await companyAPI.updateProfile(form)
    await auth.refreshMe()
    saved.value = true
    setTimeout(() => { saved.value = false }, 3000)
    toast.success('Profile updated')
  } catch { toast.error('Failed to save') }
  finally { saving.value = false }
}
</script>