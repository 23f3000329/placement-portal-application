<template>
  <div class="page">
    <h4 class="mb-4 fw-semibold">My Profile</h4>

    <div v-if="loading" class="spinner-center">
      <div class="spinner-border text-success"></div>
    </div>

    <div v-else class="row g-4">

      
      <div class="col-lg-7">
        <div class="card">
          <div class="card-header fw-semibold">Personal details</div>
          <div class="card-body">
            <div v-if="saved"  class="alert alert-success py-2">✓ Profile updated</div>
            <div v-if="error"  class="alert alert-danger  py-2">{{ error }}</div>

            <div class="row g-3 mb-3">
              <div class="col-md-6">
                <label class="form-label">Full Name *</label>
                <input v-model="form.name" class="form-control" />
              </div>
              <div class="col-md-6">
                <label class="form-label">Roll Number</label>
                <input v-model="form.roll_number" class="form-control" />
              </div>
              <div class="col-md-4">
                <label class="form-label">Branch</label>
                <select v-model="form.branch" class="form-select">
                  <option value="">Select</option>
                  <option v-for="b in branches" :key="b">{{ b }}</option>
                </select>
              </div>
              <div class="col-md-4">
                <label class="form-label">Year</label>
                <select v-model="form.year" class="form-select">
                  <option value="">Select</option>
                  <option v-for="y in [1,2,3,4]" :key="y" :value="y">Year {{ y }}</option>
                </select>
              </div>
              <div class="col-md-4">
                <label class="form-label">CGPA</label>
                <input v-model.number="form.cgpa" type="number" step="0.01" min="0" max="10"
                  class="form-control" placeholder="8.5" />
              </div>
              <div class="col-md-6">
                <label class="form-label">Phone</label>
                <input v-model="form.phone" class="form-control" placeholder="9876543210" />
              </div>
              <div class="col-md-6">
                <label class="form-label">Skills <small class="text-secondary">(comma-separated)</small></label>
                <input v-model="form.skills" class="form-control" placeholder="Python, React, SQL" />
              </div>
              <div class="col-md-6">
                <label class="form-label">LinkedIn</label>
                <input v-model="form.linkedin" class="form-control" placeholder="linkedin.com/in/…" />
              </div>
              <div class="col-md-6">
                <label class="form-label">GitHub</label>
                <input v-model="form.github" class="form-control" placeholder="github.com/…" />
              </div>
            </div>

            <button class="btn btn-success" :disabled="saving" @click="saveProfile">
              <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
              {{ saving ? 'Saving…' : 'Save changes' }}
            </button>
          </div>
        </div>
      </div>

      
      <div class="col-lg-5">

        
        <div class="card mb-3">
          <div class="card-header fw-semibold">Resume</div>
          <div class="card-body">
            <div v-if="resumePath" class="alert alert-success py-2 small mb-3">
              <i class="bi bi-file-earmark-check me-1"></i>Resume on file
            </div>
            <div v-else class="alert alert-warning py-2 small mb-3">
              <i class="bi bi-exclamation-triangle me-1"></i>No resume uploaded yet
            </div>

            <div class="mb-3">
              <label class="form-label small">Upload resume <span class="text-secondary">(PDF, DOC, DOCX — max 5 MB)</span></label>
              <input type="file" accept=".pdf,.doc,.docx" class="form-control form-control-sm" @change="handleFile" />
            </div>

            <div v-if="uploadError"   class="alert alert-danger  py-2 small mb-2">{{ uploadError }}</div>
            <div v-if="uploadSuccess" class="alert alert-success py-2 small mb-2">{{ uploadSuccess }}</div>

            <button class="btn btn-success btn-sm" :disabled="!resumeFile || uploading" @click="uploadResume">
              <span v-if="uploading" class="spinner-border spinner-border-sm me-2"></span>
              {{ uploading ? 'Uploading…' : 'Upload resume' }}
            </button>
          </div>
        </div>

        
        <div class="card">
          <div class="card-header fw-semibold">Skills & completeness</div>
          <div class="card-body">
            <div v-if="!skillList.length" class="text-secondary small mb-3">
              Add skills in the form on the left
            </div>
            <div v-else class="d-flex flex-wrap gap-1 mb-3">
              <span v-for="s in skillList" :key="s" class="badge bg-success bg-opacity-75">{{ s }}</span>
            </div>

            <div class="section-label">Profile completeness — {{ completeness }}%</div>
            <div class="progress progress-thin">
              <div class="progress-bar bg-success" :style="`width:${completeness}%`"></div>
            </div>
            <div class="text-secondary small mt-1">
              Fill all fields and upload a resume to reach 100%
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { api, apiUpload } from '../../main.js'

const loading       = ref(true)
const saving        = ref(false)
const saved         = ref(false)
const error         = ref('')
const uploading     = ref(false)
const resumeFile    = ref(null)
const resumePath    = ref('')
const uploadError   = ref('')
const uploadSuccess = ref('')

const branches = ['CSE','ECE','IT','DS','ME','EEE','Civil','Chemical']

const form = reactive({
  name:'', roll_number:'', branch:'', year:'', cgpa:'',
  phone:'', skills:'', linkedin:'', github:'',
})

onMounted(async () => {
  try {
    const data = await api('/student/profile')
    Object.assign(form, data)
    resumePath.value = data.resume_path || ''
  } catch (e) { error.value = 'Failed to load profile: ' + e.message }
  finally { loading.value = false }
})

const skillList = computed(() =>
  form.skills ? form.skills.split(',').map(s => s.trim()).filter(Boolean) : []
)

const completeness = computed(() => {
  const fields  = ['name','roll_number','branch','year','cgpa','phone','skills','linkedin','github']
  const filled  = fields.filter(f => form[f]).length
  const hasResume = resumePath.value ? 1 : 0
  return Math.round(((filled + hasResume) / (fields.length + 1)) * 100)
})

async function saveProfile() {
  error.value = ''
  if (!form.name) { error.value = 'Name is required'; return }
  saving.value = true
  try {
    const updated = await api('/student/profile', {
      method: 'PUT',
      body: JSON.stringify({ ...form, year: form.year ? Number(form.year) : null, cgpa: form.cgpa ? Number(form.cgpa) : null })
    })
    Object.assign(form, updated)
    localStorage.setItem('profile', JSON.stringify(updated))
    saved.value = true
    setTimeout(() => { saved.value = false }, 3000)
  } catch (e) { error.value = e.message }
  finally { saving.value = false }
}

function handleFile(e) { resumeFile.value = e.target.files[0] }

async function uploadResume() {
  if (!resumeFile.value) return
  uploadError.value = ''; uploadSuccess.value = ''
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('resume', resumeFile.value)
    const data = await apiUpload('/student/profile/resume', fd)
    resumePath.value    = data.filename || 'uploaded'
    uploadSuccess.value = '✓ Resume uploaded successfully'
    resumeFile.value    = null
  } catch (e) { uploadError.value = e.message }
  finally { uploading.value = false }
}
</script>

<style scoped>
.section-label {
  font-size: 0.72rem; font-weight: 600; color: var(--bs-secondary-color);
  text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.4rem;
}
</style>
