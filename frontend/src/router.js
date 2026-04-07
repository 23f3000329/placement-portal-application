import { createRouter, createWebHistory } from 'vue-router'

import Login from './views/Login.vue'
import Admin from './views/AdminDashboard.vue'
import Company from './views/CompanyDashboard.vue'
import Student from './views/StudentDashboard.vue'

const routes = [
  { path: '/', component: Login },
  { path: '/admin', component: Admin },
  { path: '/company', component: Company },
  { path: '/student', component: Student }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router