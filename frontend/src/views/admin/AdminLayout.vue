<template>
  <div class="d-flex">
    <!-- Sidebar -->
    <aside class="sidebar bg-dark border-end border-secondary">
      <div class="sidebar-logo">
        <i class="bi bi-mortarboard-fill text-success me-2"></i>Placement<span>Portal</span>
      </div>
      <nav class="sidebar-nav">
        <RouterLink to="/admin/dashboard"     class="nav-item-link"><i class="bi bi-speedometer2 me-2"></i>Dashboard</RouterLink>
        <RouterLink to="/admin/companies"     class="nav-item-link"><i class="bi bi-building me-2"></i>Companies</RouterLink>
        <RouterLink to="/admin/students"      class="nav-item-link"><i class="bi bi-people me-2"></i>Students</RouterLink>
        <RouterLink to="/admin/drives"        class="nav-item-link"><i class="bi bi-briefcase me-2"></i>Drives</RouterLink>
        <RouterLink to="/admin/applications"  class="nav-item-link"><i class="bi bi-file-earmark-text me-2"></i>Applications</RouterLink>
      </nav>
      <div class="sidebar-footer">
        <div class="text-secondary small mb-2">
          <i class="bi bi-shield-lock me-1"></i>Admin
        </div>
        <button class="btn btn-outline-danger btn-sm w-100" @click="logout">
          <i class="bi bi-box-arrow-right me-1"></i>Logout
        </button>
      </div>
    </aside>

    <!-- Main content -->
    <div class="main-content flex-grow-1">
      <RouterView />
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
function logout() { localStorage.clear(); router.push('/login') }
</script>
