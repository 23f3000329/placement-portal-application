<template>
  <div class="page">
    <button class="btn btn-sm" style="margin-bottom:16px" @click="$router.back()">← Back</button>

    <div v-if="loading" class="spinner"></div>

    <template v-else-if="drive">
      <div style="display:grid;grid-template-columns:1fr 340px;gap:20px;align-items:start">
        <!-- Left: details -->
        <div>
          <div class="card" style="margin-bottom:16px">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px">
              <div>
                <h2>{{ drive.title }}</h2>
                <div style="color:var(--text2);margin-top:4px">
                  {{ drive.company_name }} · {{ drive.company_industry }}
                </div>
              </div>
              <StatusBadge :status="drive.status" />
            </div>

            <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px">
              <span class="pill">{{ drive.job_type }}</span>
              <span class="pill">{{ drive.location || 'Remote' }}</span>
              <span class="pill">{{ drive.interview_mode }}</span>
              <span v-if="drive.salary_min" class="pill">
                ₹{{ fmtSalary(drive.salary_min) }}
                {{ drive.salary_max ? '– ₹' + fmtSalary(drive.salary_max) : '+' }} p.a.
              </span>
            </div>

            <div style="margin-bottom:16px">
              <div style="font-size:0.75rem;font-weight:500;color:var(--text2);text-transform:uppercase;letter-spacing:.4px;margin-bottom:6px">
                Job Description
              </div>
              <p style="font-size:0.9rem;line-height:1.7;white-space:pre-wrap">{{ drive.job_description || 'No description provided.' }}</p>
            </div>

            <div v-if="drive.skills_required" style="margin-bottom:16px">
              <div style="font-size:0.75rem;font-weight:500;color:var(--text2);text-transform:uppercase;letter-spacing:.4px;margin-bottom:6px">
                Skills Required
              </div>
              <div style="display:flex;gap:6px;flex-wrap:wrap">
                <span v-for="s in drive.skills_required.split(',')" :key="s" class="pill">{{ s.trim() }}</span>
              </div>
            </div>
          </div>

          <!-- Eligibility criteria -->
          <div class="card">
            <div class="card-header"><span class="card-title">Eligibility criteria</span></div>
            <table style="font-size:0.88rem">
              <tbody>
                <tr>
                  <td style="padding:8px 0;color:var(--text2);width:160px">Minimum CGPA</td>
                  <td style="padding:8px 0;font-weight:600">{{ drive.min_cgpa || 'None' }}</td>
                </tr>
                <tr>
                  <td style="padding:8px 0;color:var(--text2)">Eligible branches</td>
                  <td style="padding:8px 0">
                    <span v-if="!drive.eligible_branches?.length">All branches</span>
                    <span v-for="b in drive.eligible_branches" :key="b" class="pill" style="margin:2px">{{ b }}</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:8px 0;color:var(--text2)">Application deadline</td>
                  <td style="padding:8px 0;font-weight:600" :style="isDeadlineSoon(drive.application_deadline) ? 'color:var(--red)' : ''">
                    {{ fmtDate(drive.application_deadline) || 'Open' }}
                    <span v-if="isDeadlineSoon(drive.application_deadline)"> ⚠ Closing soon</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Right: apply card -->
        <div>
          <!-- Already applied -->
          <div v-if="drive.already_applied && drive.application" class="card">
            <div class="card-header"><span class="card-title">Your application</span></div>
            <div style="margin-bottom:14px">
              <div style="font-size:0.78rem;color:var(--text2);margin-bottom:4px;text-transform:uppercase;letter-spacing:.4px">Status</div>
              <StatusBadge :status="drive.application.status" />
            </div>
            <div v-if="drive.application.interview_date" style="margin-bottom:14px">
              <div style="font-size:0.78rem;color:var(--text2);margin-bottom:4px;text-transform:uppercase;letter-spacing:.4px">Interview</div>
              <div style="font-weight:600">{{ fmtDate(drive.application.interview_date) }}</div>
            </div>
            <div v-if="drive.application.company_feedback" style="margin-bottom:14px">
              <div style="font-size:0.78rem;color:var(--text2);margin-bottom:4px;text-transform:uppercase;letter-spacing:.4px">Feedback</div>
              <p style="font-size:0.88rem">{{ drive.application.company_feedback }}</p>
            </div>
            <div style="font-size:0.78rem;color:var(--text2)">
              Applied {{ fmtDate(drive.application.applied_at) }}
            </div>
          </div>

          <!-- Not yet applied -->
          <div v-else class="card">
            <div class="card-header"><span class="card-title">Apply for this drive</span></div>
            <div v-if="!drive.is_eligible" style="background:var(--red-bg);color:var(--red-text);padding:10px 12px;border-radius:var(--radius);margin-bottom:14px;font-size:0.85rem">
              ✕ You don't meet the eligibility criteria for this drive.
            </div>
            <div v-else style="background:var(--green-bg);color:var(--green-text);padding:10px 12px;border-radius:var(--radius);margin-bottom:14px;font-size:0.85rem">
              ✓ You meet the eligibility criteria
            </div>

            <div style="font-size:0.85rem;color:var(--text2);margin-bottom:16px">
              Your profile (CGPA {{ profile?.cgpa }}, {{ profile?.branch }}) will be shared with {{ drive.company_name }}.
            </div>

            <button
              class="btn btn-primary btn-block"
              :disabled="!drive.is_eligible || applying"
              @click="applyNow"
            >
              {{ applying ? 'Submitting…' : 'Apply now' }}
            </button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { studentAPI } from '@/services/api'
import { useAuthStore } from '@/store/auth'
import { useToastStore } from '@/store/toast'
import StatusBadge from '@/components/common/StatusBadge.vue'

const route   = useRoute()
const router  = useRouter()
const auth    = useAuthStore()
const toast   = useToastStore()
const drive   = ref(null)
const loading = ref(false)
const applying = ref(false)
const profile  = auth.profile

onMounted(async () => {
  loading.value = true
  try { const { data } = await studentAPI.getDrive(route.params.id); drive.value = data }
  catch { toast.error('Drive not found'); router.push('/student/drives') }
  finally { loading.value = false }
})

async function applyNow() {
  applying.value = true
  try {
    await studentAPI.applyDrive(drive.value.id)
    toast.success('Application submitted successfully!')
    const { data } = await studentAPI.getDrive(drive.value.id)
    drive.value = data
  } catch (e) {
    toast.error(e.response?.data?.error || 'Application failed')
  } finally { applying.value = false }
}

function isDeadlineSoon(d) { return d && (new Date(d) - new Date()) < 3 * 86400000 }
function fmtSalary(v) {
  if (!v) return ''
  return v >= 100000 ? (v/100000).toFixed(1)+'L' : v.toLocaleString()
}
function fmtDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('en-IN', { day:'numeric', month:'short', year:'numeric' })
}
</script>