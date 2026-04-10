<template>
  <div class="layout">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-logo">Placement<span>Portal</span></div>
      <nav class="sidebar-nav">
        <RouterLink to="/admin/dashboard"    class="nav-item" active-class="active"><span class="nav-icon">📊</span> Dashboard</RouterLink>
        <RouterLink to="/admin/companies"    class="nav-item" active-class="active"><span class="nav-icon">🏢</span> Companies</RouterLink>
        <RouterLink to="/admin/students"     class="nav-item" active-class="active"><span class="nav-icon">🎓</span> Students</RouterLink>
        <RouterLink to="/admin/drives"       class="nav-item" active-class="active"><span class="nav-icon">📋</span> Drives</RouterLink>
        <RouterLink to="/admin/applications" class="nav-item" active-class="active"><span class="nav-icon">📝</span> Applications</RouterLink>
      </nav>
      <div class="sidebar-footer">
        <div style="font-size:0.8rem;color:var(--text2);margin-bottom:8px">Admin</div>
        <button class="btn btn-sm btn-block" @click="logout">Logout</button>
      </div>
    </aside>
    <!-- Main -->
    <div class="main-content">
      <RouterView />
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
function logout() {
  localStorage.clear()
  router.push('/login')
}
</script>
