<template>
  <div class="page">
    <h2 style="margin-bottom:20px">My Profile</h2>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:start">
      <!-- Edit form -->
      <div class="card">
        <div style="display:flex;align-items:center;gap:14px;margin-bottom:20px;padding-bottom:16px;border-bottom:1px solid var(--border)">
          <div class="avatar avatar-lg" style="background:var(--teal-bg);color:var(--teal-text)">
            {{ initials(form.name) }}
          </div>
          <div>
            <div style="font-size:1rem;font-weight:600">{{ form.name || '—' }}</div>
            <div style="font-size:0.82rem;color:var(--text2)">{{ auth.user?.email }}</div>
            <span v-if="auth.profile?.is_placed" class="badge badge-green" style="margin-top:4px">Placed ✓</span>
          </div>
        </div>

        <div v-if="saved" style="background:var(--green-bg);color:var(--green-text);padding:10px 12px;border-radius:var(--radius);margin-bottom:14px;font-size:0.88rem">
          ✓ Profile updated
        </div>

        <div class="form-grid-2">
          <div class="form-group">
            <label>Full name *</label>
            <input v-model="form.name" class="form-control" />
          </div>
          <div class="form-group">
            <label>Roll number</label>
            <input v-model="form.roll_number" class="form-control" />
          </div>
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
              <option v-for="y in [1,2,3,4]" :key="y" :value="y">{{ y }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>CGPA</label>
            <input v-model="form.cgpa" type="number" step="0.01" min="0" max="10" class="form-control" />
          </div>
        </div>
        <div class="form-group">
          <label>Phone</label>
          <input v-model="form.phone" class="form-control" placeholder="9876543210" />
        </div>
        <div class="form-group">
          <label>Skills (comma-separated)</label>
          <input v-model="form.skills" class="form-control" placeholder="Python, React, SQL, ML" />
        </div>
        <div class="form-grid-2">
          <div class="form-group">
            <label>LinkedIn</label>
            <input v-model="form.linkedin" class="form-control" placeholder="linkedin.com/in/…" />
          </div>
          <div class="form-group">
            <label>GitHub</label>
            <input v-model="form.github" class="form-control" placeholder="github.com/…" />
          </div>
        </div>
        <button class="btn btn-primary" :disabled="saving" @click="saveProfile">
          {{ saving ? 'Saving…' : 'Save changes' }}
        </button>
      </div>

      <!-- Resume upload -->
      <div>
        <div class="card" style="margin-bottom:16px">
          <div class="card-header"><span class="card-title">Resume</span></div>
          <div v-if="auth.profile?.resume_path" style="background:var(--green-bg);color:var(--green-text);padding:10px 12px;border-radius:var(--radius);margin-bottom:12px;font-size:0.85rem">
            ✓ Resume uploaded: {{ auth.profile.resume_path }}
          </div>
          <div v-else style="background:var(--amber-bg);color:var(--amber-text);padding:10px 12px;border-radius:var(--radius);margin-bottom:12px;font-size:0.85rem">
            ⚠ No resume uploaded yet
          </div>
          <div class="form-group">
            <label>Upload resume (PDF, DOC, DOCX — max 5 MB)</label>
            <input type="file" accept=".pdf,.doc,.docx" class="form-control" @change="handleFile" />
          </div>
          <button class="btn btn-primary btn-sm" :disabled="!resumeFile || uploading" @click="uploadResume">
            {{ uploading ? 'Uploading…' : 'Upload' }}
          </button>
        </div>

        <!-- Skills display -->
        <div class="card">
          <div class="card-header"><span class="card-title">Skills</span></div>
          <div v-if="!form.skills" style="color:var(--text3);font-size:0.88rem">No skills added yet</div>
          <div style="display:flex;gap:6px;flex-wrap:wrap">
            <span v-for="s in skillList" :key="s" class="pill" style="background:var(--green-bg);color:var(--green-text);border-color:#9FE1CB">
              {{ s }}
            </span>
          </div>
          <div style="margin-top:16px">
            <div style="font-size:0.78rem;font-weight:500;color:var(--text2);text-transform:uppercase;letter-spacing:.4px;margin-bottom:4px">Profile completeness</div>
            <div class="progress-wrap">
              <div class="progress-bar" :style="`width:${completeness}%;background:var(--green)`"></div>
            </div>
            <div style="font-size:0.78rem;color:var(--text2);margin-top:4px">{{ completeness }}% complete</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { studentAPI } from '@/services/api'
import { useAuthStore } from '@/store/auth'
import { useToastStore } from '@/store/toast'

const auth       = useAuthStore()
const toast      = useToastStore()
const saving     = ref(false)
const saved      = ref(false)
const uploading  = ref(false)
const resumeFile = ref(null)
const branches   = ['CSE','ECE','IT','DS','ME','EEE','Civil','Chemical']

const form = reactive({
  name:'', roll_number:'', branch:'', year:'', cgpa:'',
  phone:'', skills:'', linkedin:'', github:'',
})

onMounted(async () => {
  try {
    const { data } = await studentAPI.getProfile()
    Object.assign(form, { ...data, year: data.year || '', cgpa: data.cgpa || '' })
  } catch { toast.error('Failed to load profile') }
})

function initials(n) { return n?.split(' ').map(w=>w[0]).join('').toUpperCase().slice(0,2) || 'ST' }

const skillList = computed(() =>
  form.skills ? form.skills.split(',').map(s => s.trim()).filter(Boolean) : []
)

const completeness = computed(() => {
  const fields = ['name','roll_number','branch','year','cgpa','phone','skills','linkedin','github']
  const filled = fields.filter(f => form[f]).length
  const hasResume = auth.profile?.resume_path ? 1 : 0
  return Math.round(((filled + hasResume) / (fields.length + 1)) * 100)
})

async function saveProfile() {
  if (!form.name) { toast.error('Name is required'); return }
  saving.value = true
  try {
    await studentAPI.updateProfile({
      ...form, year: form.year ? +form.year : null, cgpa: form.cgpa ? +form.cgpa : null
    })
    await auth.refreshMe()
    saved.value = true
    setTimeout(() => { saved.value = false }, 3000)
    toast.success('Profile updated')
  } catch { toast.error('Failed to save profile') }
  finally { saving.value = false }
}

function handleFile(e) { resumeFile.value = e.target.files[0] }

async function uploadResume() {
  if (!resumeFile.value) return
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('resume', resumeFile.value)
    await studentAPI.uploadResume(fd)
    await auth.refreshMe()
    toast.success('Resume uploaded successfully')
  } catch (e) {
    toast.error(e.response?.data?.error || 'Upload failed')
  } finally { uploading.value = false }
}
</script>