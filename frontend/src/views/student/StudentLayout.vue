<template>
  <div class="d-flex">
    <aside class="sidebar bg-dark border-end border-secondary">
      <div class="sidebar-logo">
        <i class="bi bi-mortarboard-fill text-success me-2"></i>Placement<span>Portal</span>
      </div>
      <nav class="sidebar-nav">
        <RouterLink to="/student/dashboard"    class="nav-item-link"><i class="bi bi-speedometer2 me-2"></i>Dashboard</RouterLink>
        <RouterLink to="/student/drives"       class="nav-item-link"><i class="bi bi-briefcase me-2"></i>Browse Drives</RouterLink>
        <RouterLink to="/student/applications" class="nav-item-link"><i class="bi bi-file-earmark-text me-2"></i>My Applications</RouterLink>
        <RouterLink to="/student/profile"      class="nav-item-link"><i class="bi bi-person-circle me-2"></i>Profile</RouterLink>
      </nav>
      <div class="sidebar-footer">
        <div class="text-secondary small mb-2 text-truncate">{{ studentName }}</div>
        <button class="btn btn-outline-danger btn-sm w-100" @click="logout">
          <i class="bi bi-box-arrow-right me-1"></i>Logout
        </button>
      </div>
    </aside>
    <div class="main-content flex-grow-1">
      <RouterView />
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router     = useRouter()
const profile    = JSON.parse(localStorage.getItem('profile') || '{}')
const studentName = profile.name || 'Student'
function logout() { localStorage.clear(); router.push('/login') }
</script>
