<template>
  <div class="layout">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-logo">Placement<span>Portal</span></div>
      <nav class="sidebar-nav">
        <RouterLink
          v-for="item in navItems" :key="item.to"
          :to="item.to"
          custom
          v-slot="{ isActive, navigate }"
        >
          <div :class="['nav-item', isActive && 'active']" @click="navigate">
            <span class="nav-icon">{{ item.icon }}</span>
            {{ item.label }}
          </div>
        </RouterLink>
      </nav>
      <div class="sidebar-footer">
        <div style="font-size:0.78rem;color:var(--text2);margin-bottom:8px">
          Signed in as<br>
          <strong style="color:var(--text)">{{ auth.user?.email }}</strong>
        </div>
        <button class="btn btn-sm btn-danger btn-block" @click="handleLogout">Sign out</button>
      </div>
    </aside>

    <!-- Main -->
    <div class="main-content">
      <div class="topbar">
        <div>
          <span style="font-weight:600">Admin Panel</span>
          <span style="color:var(--text2);margin-left:8px;font-size:0.85rem">Institute Placement Cell</span>
        </div>
        <div class="avatar" style="background:var(--green-bg);color:var(--green-text)">AD</div>
      </div>
      <RouterView />
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const auth   = useAuthStore()

const navItems = [
  { to: '/admin/dashboard',    icon: '◼', label: 'Dashboard' },
  { to: '/admin/companies',    icon: '🏢', label: 'Companies' },
  { to: '/admin/students',     icon: '🎓', label: 'Students' },
  { to: '/admin/drives',       icon: '📋', label: 'Drives' },
  { to: '/admin/applications', icon: '📄', label: 'Applications' },
]

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}
</script>