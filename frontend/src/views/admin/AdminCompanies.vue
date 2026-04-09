<template>
  <div class="page">
    <h2 style="margin-bottom:20px">Companies</h2>

    <div class="search-bar">
      <input v-model="query" placeholder="Search by name…" @input="fetch" />
      <select v-model="statusFilter" @change="fetch">
        <option value="all">All statuses</option>
        <option value="pending">Pending</option>
        <option value="approved">Approved</option>
        <option value="rejected">Rejected</option>
      </select>
    </div>

    <div v-if="loading" class="spinner"></div>

    <div v-else-if="!companies.length" class="empty-state">
      <div class="icon">🏢</div>
      <p>No companies found</p>
    </div>

    <div v-else class="card" style="padding:0;overflow:hidden">
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Company</th>
              <th>Industry</th>
              <th>HR Contact</th>
              <th>Drives</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in companies" :key="c.id">
              <td>
                <div style="font-weight:600">{{ c.name }}</div>
                <small>{{ c.email }}</small><br>
                <small v-if="c.website">{{ c.website }}</small>
              </td>
              <td>{{ c.industry || '—' }}</td>
              <td>{{ c.hr_name || '—' }}</td>
              <td>{{ c.drives_count }}</td>
              <td>
                <StatusBadge :status="c.is_blacklisted ? 'blacklisted' : c.approval_status" />
              </td>
              <td>
                <div style="display:flex;gap:6px;flex-wrap:wrap">
                  <template v-if="c.approval_status === 'pending'">
                    <button class="btn btn-sm btn-success" @click="action(c.id,'approve')">Approve</button>
                    <button class="btn btn-sm btn-danger"  @click="action(c.id,'reject')">Reject</button>
                  </template>
                  <template v-else-if="c.approval_status === 'approved'">
                    <button v-if="!c.is_blacklisted" class="btn btn-sm btn-danger"
                      @click="confirm('blacklist', c)">Blacklist</button>
                    <button v-else class="btn btn-sm btn-success"
                      @click="action(c.id,'activate')">Restore</button>
                  </template>
                  <template v-else-if="c.approval_status === 'rejected'">
                    <button class="btn btn-sm btn-success" @click="action(c.id,'approve')">Approve</button>
                  </template>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <ConfirmModal
      v-if="modal.show"
      :title="modal.title"
      :message="modal.message"
      confirm-label="Confirm"
      confirm-class="btn-danger"
      @confirm="runModal"
      @cancel="modal.show = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminAPI } from '@/services/api'
import { useToastStore } from '@/store/toast'
import StatusBadge from '@/components/common/StatusBadge.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'

const toast        = useToastStore()
const companies    = ref([])
const loading      = ref(false)
const query        = ref('')
const statusFilter = ref('all')
const modal        = ref({ show: false, title: '', message: '', cb: null })

onMounted(fetch)

async function fetch() {
  loading.value = true
  try {
    const { data } = await adminAPI.getCompanies({ q: query.value, status: statusFilter.value })
    companies.value = data
  } catch { toast.error('Failed to load companies') }
  finally { loading.value = false }
}

async function action(id, type) {
  try {
    const map = {
      approve:   adminAPI.approveCompany,
      reject:    adminAPI.rejectCompany,
      blacklist: adminAPI.blacklistCompany,
      activate:  adminAPI.activateCompany,
    }
    await map[type](id)
    const labels = { approve:'Approved', reject:'Rejected', blacklist:'Blacklisted', activate:'Restored' }
    toast.success(labels[type] + ' successfully')
    fetch()
  } catch { toast.error('Action failed') }
}

function confirm(type, company) {
  modal.value = {
    show: true,
    title: `Blacklist ${company.name}?`,
    message: 'This will close all their placement drives. Students will no longer see their drives.',
    cb: () => action(company.id, type)
  }
}

function runModal() {
  modal.value.cb?.()
  modal.value.show = false
}
</script>