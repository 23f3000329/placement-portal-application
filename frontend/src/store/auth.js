import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const user    = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const profile = ref(JSON.parse(localStorage.getItem('profile') || 'null'))

  const isLoggedIn  = computed(() => !!user.value)
  const role        = computed(() => user.value?.role || null)
  const isAdmin     = computed(() => role.value === 'admin')
  const isCompany   = computed(() => role.value === 'company')
  const isStudent   = computed(() => role.value === 'student')

  function _persist(data) {
    user.value    = data.user
    profile.value = data.profile
    localStorage.setItem('user',    JSON.stringify(data.user))
    localStorage.setItem('profile', JSON.stringify(data.profile))
    localStorage.setItem('access_token',  data.access_token)
    if (data.refresh_token)
      localStorage.setItem('refresh_token', data.refresh_token)
  }

  async function login(email, password) {
    const { data } = await authAPI.loginUser({ email, password })
    _persist(data)
    return data
  }

  async function registerStudent(payload) {
    const { data } = await authAPI.registerStudent(payload)
    _persist(data)
    return data
  }

  async function registerCompany(payload) {
    const { data } = await authAPI.registerCompany(payload)
    return data  // company must wait for approval, no token
  }

  async function logout() {
    try { await authAPI.logout() } catch {}
    user.value    = null
    profile.value = null
    localStorage.clear()
  }

  async function refreshMe() {
    const { data } = await authAPI.me()
    user.value    = data.user
    profile.value = data.profile
    localStorage.setItem('user',    JSON.stringify(data.user))
    localStorage.setItem('profile', JSON.stringify(data.profile))
  }

  return { user, profile, isLoggedIn, role, isAdmin, isCompany, isStudent,
           login, registerStudent, registerCompany, logout, refreshMe }
})