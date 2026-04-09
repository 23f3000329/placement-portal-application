<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="sidebar-logo">Placement<span>Portal</span></div>
      <nav class="sidebar-nav">
        <RouterLink v-for="item in navItems" :key="item.to" :to="item.to" custom v-slot="{ isActive, navigate }">
          <div :class="['nav-item', isActive && 'active']" @click="navigate">
            <span class="nav-icon">{{ item.icon }}</span>{{ item.label }}
          </div>
        </RouterLink>
      </nav>
      <div class="sidebar-footer">
        <div style="font-size:0.78rem;color:var(--text2);margin-bottom:8px">
          {{ auth.profile?.name }}<br>
          <span class="badge badge-green" style="margin-top:4px">Approved</span>
        </div>
        <button class="btn btn-sm btn-danger btn-block" @click="handleLogout">Sign out</button>
      </div>
    </aside>
    <div class="main-content">
      <div class="topbar">
        <div>
          <span style="font-weight:600">{{ auth.profile?.name || 'Company' }}</span>
          <span style="color:var(--text2);margin-left:8px;font-size:0.85rem">{{ auth.profile?.industry }}</span>
        </div>
        <div class="avatar" style="background:var(--blue-bg);color:var(--blue-text)">
          {{ initials(auth.profile?.name) }}
        </div>
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
  { to: '/company/dashboard', icon: '◼', label: 'Dashboard' },
  { to: '/company/drives',    icon: '📋', label: 'My Drives' },
  { to: '/company/profile',   icon: '🏢', label: 'Profile' },
]

function initials(n) { return n?.split(' ').map(w=>w[0]).join('').toUpperCase().slice(0,2) || 'CO' }
async function handleLogout() { await auth.logout(); router.push('/login') }
</script>