<template>
  <div class="container mt-5">
    <h2>Student Dashboard</h2>

    <button @click="loadJobs" class="btn btn-primary mb-3">
      Load Jobs
    </button>

    <ul>
      <li v-for="job in jobs" :key="job.id">
        {{ job.title }} (CGPA: {{ job.cgpa_required }})

        <button @click="apply(job.id)" class="btn btn-success btn-sm ms-2">
          Apply
        </button>
      </li>
    </ul>

    <hr />

    <button @click="loadApplications" class="btn btn-secondary mb-3">
      My Applications
    </button>

    <ul>
      <li v-for="app in applications" :key="app.job_id">
        Job {{ app.job_id }} - {{ app.status }}
      </li>
    </ul>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      jobs: [],
      applications: []
    }
  },
  methods: {
    async loadJobs() {
      const res = await axios.get('http://127.0.0.1:5000/api/student/jobs', {
        headers: {
          Authorization: "Bearer " + localStorage.getItem("token")
        }
      })
      this.jobs = res.data
    },

    async apply(jobId) {
      try {
        await axios.post(`http://127.0.0.1:5000/api/student/apply/${jobId}`, {}, {
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token")
          }
        })
        alert("Applied successfully")
      } catch (err) {
        alert("Error: " + err.response.data.error)
      }
    },

    async loadApplications() {
      const res = await axios.get('http://127.0.0.1:5000/api/student/applications', {
        headers: {
          Authorization: "Bearer " + localStorage.getItem("token")
        }
      })
      this.applications = res.data
    }
  }
}
</script>