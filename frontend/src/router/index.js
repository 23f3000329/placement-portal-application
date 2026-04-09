import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/login' },

  // Auth
  { path: '/login',            name: 'Login',           component: () => import('@/views/LoginView.vue') },
  { path: '/register/student', name: 'RegisterStudent', component: () => import('@/views/RegisterStudent.vue') },
  { path: '/register/company', name: 'RegisterCompany', component: () => import('@/views/RegisterCompany.vue') },

  // Admin
  {
    path: '/admin',
    component: () => import('@/views/admin/AdminLayout.vue'),
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      { path: '',          redirect: '/admin/dashboard' },
      { path: 'dashboard', name: 'AdminDashboard', component: () => import('@/views/admin/AdminDashboard.vue') },
      { path: 'companies', name: 'AdminCompanies', component: () => import('@/views/admin/AdminCompanies.vue') },
      { path: 'students',  name: 'AdminStudents',  component: () => import('@/views/admin/AdminStudents.vue') },
      { path: 'drives',    name: 'AdminDrives',    component: () => import('@/views/admin/AdminDrives.vue') },
      { path: 'applications', name: 'AdminApplications', component: () => import('@/views/admin/AdminApplications.vue') },
    ]
  },

  // Company
  {
    path: '/company',
    component: () => import('@/views/company/CompanyLayout.vue'),
    meta: { requiresAuth: true, role: 'company' },
    children: [
      { path: '',          redirect: '/company/dashboard' },
      { path: 'dashboard', name: 'CompanyDashboard', component: () => import('@/views/company/CompanyDashboard.vue') },
      { path: 'drives',    name: 'CompanyDrives',    component: () => import('@/views/company/CompanyDrives.vue') },
      { path: 'drives/:id/applicants', name: 'CompanyApplicants', component: () => import('@/views/company/CompanyApplicants.vue') },
      { path: 'profile',   name: 'CompanyProfile',   component: () => import('@/views/company/CompanyProfile.vue') },
    ]
  },

  // Student
  {
    path: '/student',
    component: () => import('@/views/student/StudentLayout.vue'),
    meta: { requiresAuth: true, role: 'student' },
    children: [
      { path: '',          redirect: '/student/dashboard' },
      { path: 'dashboard', name: 'StudentDashboard',    component: () => import('@/views/student/StudentDashboard.vue') },
      { path: 'drives',    name: 'StudentDrives',       component: () => import('@/views/student/StudentDrives.vue') },
      { path: 'drives/:id',name: 'StudentDriveDetail',  component: () => import('@/views/student/StudentDriveDetail.vue') },
      { path: 'applications', name: 'StudentApplications', component: () => import('@/views/student/StudentApplications.vue') },
      { path: 'profile',   name: 'StudentProfile',      component: () => import('@/views/student/StudentProfile.vue') },
    ]
  },

  { path: '/:pathMatch(.*)*', redirect: '/login' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  const user  = JSON.parse(localStorage.getItem('user') || 'null')

  if (to.meta.requiresAuth) {
    if (!token || !user) return next('/login')
    if (to.meta.role && user.role !== to.meta.role) {
      // Redirect to correct dashboard
      const map = { admin: '/admin', company: '/company', student: '/student' }
      return next(map[user.role] || '/login')
    }
  }

  // If already logged in, redirect away from auth pages
  if (['/login','/register/student','/register/company'].includes(to.path) && token && user) {
    const map = { admin: '/admin', company: '/company', student: '/student' }
    return next(map[user.role] || '/')
  }

  next()
})

export default router