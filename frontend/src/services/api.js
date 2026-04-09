import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT on every request
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Auto-refresh on 401
api.interceptors.response.use(
  res => res,
  async err => {
    const original = err.config
    if (err.response?.status === 401 && !original._retry) {
      original._retry = true
      const refresh = localStorage.getItem('refresh_token')
      if (refresh) {
        try {
          const { data } = await axios.post('/api/auth/refresh', {}, {
            headers: { Authorization: `Bearer ${refresh}` }
          })
          localStorage.setItem('access_token', data.access_token)
          original.headers.Authorization = `Bearer ${data.access_token}`
          return api(original)
        } catch {
          localStorage.clear()
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(err)
  }
)

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authAPI = {
  loginUser:         data => api.post('/auth/login', data),
  registerStudent:   data => api.post('/auth/register/student', data),
  registerCompany:   data => api.post('/auth/register/company', data),
  logout:            ()   => api.delete('/auth/logout'),
  me:                ()   => api.get('/auth/me'),
}

// ── Admin ─────────────────────────────────────────────────────────────────────
export const adminAPI = {
  getStats:          ()         => api.get('/admin/stats'),
  getCharts:         ()         => api.get('/admin/charts'),
  getCompanies:      (params)   => api.get('/admin/companies', { params }),
  approveCompany:    id         => api.patch(`/admin/companies/${id}/approve`),
  rejectCompany:     id         => api.patch(`/admin/companies/${id}/reject`),
  blacklistCompany:  id         => api.patch(`/admin/companies/${id}/blacklist`),
  activateCompany:   id         => api.patch(`/admin/companies/${id}/activate`),
  getStudents:       (params)   => api.get('/admin/students', { params }),
  blacklistStudent:  id         => api.patch(`/admin/students/${id}/blacklist`),
  activateStudent:   id         => api.patch(`/admin/students/${id}/activate`),
  getDrives:         (params)   => api.get('/admin/drives', { params }),
  approveDrive:      id         => api.patch(`/admin/drives/${id}/approve`),
  rejectDrive:       id         => api.patch(`/admin/drives/${id}/reject`),
  getApplications:   ()         => api.get('/admin/applications'),
}

// ── Company ───────────────────────────────────────────────────────────────────
export const companyAPI = {
  getProfile:        ()         => api.get('/company/profile'),
  updateProfile:     data       => api.put('/company/profile', data),
  getStats:          ()         => api.get('/company/stats'),
  getDrives:         ()         => api.get('/company/drives'),
  createDrive:       data       => api.post('/company/drives', data),
  updateDrive:       (id, data) => api.put(`/company/drives/${id}`, data),
  getDriveApps:      id         => api.get(`/company/drives/${id}/applications`),
  updateApplication: (id, data) => api.patch(`/company/applications/${id}`, data),
}

// ── Student ───────────────────────────────────────────────────────────────────
export const studentAPI = {
  getProfile:        ()   => api.get('/student/profile'),
  updateProfile:     data => api.put('/student/profile', data),
  uploadResume:      form => api.post('/student/profile/resume', form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getDrives:         (params) => api.get('/student/drives', { params }),
  getDrive:          id       => api.get(`/student/drives/${id}`),
  applyDrive:        id       => api.post(`/student/apply/${id}`),
  getApplications:   ()       => api.get('/student/applications'),
  exportCSV:         ()       => api.post('/student/export-csv'),
  exportStatus:      taskId   => api.get(`/student/export-status/${taskId}`),
}

export default api