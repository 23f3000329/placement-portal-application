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
          <small>{{ auth.profile?.branch }} · CGPA {{ auth.profile?.cgpa }}</small>
        </div>
        <button class="btn btn-sm btn-danger btn-block" @click="handleLogout">Sign out</button>
      </div>
    </aside>
    <div class="main-content">
      <div class="topbar">
        <div>
          <span style="font-weight:600">{{ auth.profile?.name || 'Student' }}</span>
          <span style="color:var(--text2);margin-left:8px;font-size:0.85rem">{{ auth.profile?.branch }}</span>
        </div>
        <div style="display:flex;align-items:center;gap:10px">
          <span v-if="auth.profile?.is_placed" class="badge badge-green">Placed ✓</span>
          <div class="avatar" style="background:var(--teal-bg);color:var(--teal-text)">
            {{ initials(auth.profile?.name) }}
          </div>
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
  { to: '/student/dashboard',    icon: '◼', label: 'Dashboard' },
  { to: '/student/drives',       icon: '📋', label: 'Browse Drives' },
  { to: '/student/applications', icon: '📄', label: 'My Applications' },
  { to: '/student/profile',      icon: '👤', label: 'Profile' },
]

function initials(n) { return n?.split(' ').map(w=>w[0]).join('').toUpperCase().slice(0,2) || 'ST' }
async function handleLogout() { await auth.logout(); router.push('/login') }
</script>