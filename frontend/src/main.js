import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './assets/main.css'


export function getToken()   { return localStorage.getItem('access_token') }
export function getUser()    { return JSON.parse(localStorage.getItem('user') || 'null') }
export function isLoggedIn() { return !!getToken() && !!getUser() }


export async function api(path, options = {}) {
  const token = getToken()
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch('/api' + path, { ...options, headers })

  if (res.status === 401) {
    localStorage.clear()
    window.location.href = '/login'
    return
  }

  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data.error || 'Request failed')
  return data
}


export async function apiUpload(path, formData) {
  const token = getToken()
  const headers = {}
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch('/api' + path, { method: 'POST', headers, body: formData })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data.error || 'Upload failed')
  return data
}


const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/',                    redirect: '/login' },
    { path: '/login',               component: () => import('./views/LoginView.vue') },
    { path: '/register/student',    component: () => import('./views/RegisterStudent.vue') },
    { path: '/register/company',    component: () => import('./views/RegisterCompany.vue') },

    
    { path: '/admin', component: () => import('./views/admin/AdminLayout.vue'),
      meta: { role: 'admin' },
      children: [
        { path: '',            redirect: '/admin/dashboard' },
        { path: 'dashboard',   component: () => import('./views/admin/AdminDashboard.vue') },
        { path: 'companies',   component: () => import('./views/admin/AdminCompanies.vue') },
        { path: 'students',    component: () => import('./views/admin/AdminStudents.vue') },
        { path: 'drives',      component: () => import('./views/admin/AdminDrives.vue') },
        { path: 'applications',component: () => import('./views/admin/AdminApplications.vue') },
      ]
    },

    
    { path: '/company', component: () => import('./views/company/CompanyLayout.vue'),
      meta: { role: 'company' },
      children: [
        { path: '',            redirect: '/company/dashboard' },
        { path: 'dashboard',   component: () => import('./views/company/CompanyDashboard.vue') },
        { path: 'drives',      component: () => import('./views/company/CompanyDrives.vue') },
        { path: 'drives/:id/applicants', component: () => import('./views/company/CompanyApplicants.vue') },
        { path: 'profile',     component: () => import('./views/company/CompanyProfile.vue') },
      ]
    },

  
    { path: '/student', component: () => import('./views/student/StudentLayout.vue'),
      meta: { role: 'student' },
      children: [
        { path: '',            redirect: '/student/dashboard' },
        { path: 'dashboard',   component: () => import('./views/student/StudentDashboard.vue') },
        { path: 'drives',      component: () => import('./views/student/StudentDrives.vue') },
        { path: 'drives/:id',  component: () => import('./views/student/StudentDriveDetail.vue') },
        { path: 'applications',component: () => import('./views/student/StudentApplications.vue') },
        { path: 'profile',     component: () => import('./views/student/StudentProfile.vue') },
      ]
    },

    { path: '/:pathMatch(.*)*', redirect: '/login' },
  ],
  scrollBehavior: () => ({ top: 0 }),
})


router.beforeEach((to, from, next) => {
  const user = getUser()
  const token = getToken()

  const authPages = ['/login', '/register/student', '/register/company']
  if (authPages.includes(to.path) && token && user) {
    const map = { admin: '/admin', company: '/company', student: '/student' }
    return next(map[user.role] || '/')
  }

  if (to.meta.role) {
    if (!token || !user) return next('/login')
    if (user.role !== to.meta.role) {
      const map = { admin: '/admin', company: '/company', student: '/student' }
      return next(map[user.role] || '/login')
    }
  }

  next()
})

createApp(App).use(router).mount('#app')
