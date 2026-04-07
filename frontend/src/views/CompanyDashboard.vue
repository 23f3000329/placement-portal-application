<template>
  <div class="container mt-5">
    <h2>Company Dashboard</h2>

    <h4>Create Job</h4>

    <input v-model="title" placeholder="Job Title" class="form-control mb-2" />
    <input v-model="cgpa" placeholder="CGPA Required" class="form-control mb-2" />

    <button @click="createJob" class="btn btn-primary mb-3">
      Create Job
    </button>

    <hr />

    <button @click="loadJobs" class="btn btn-secondary mb-3">
      My Jobs
    </button>

    <ul>
      <li v-for="job in jobs" :key="job.id">
        {{ job.title }} - {{ job.status }}

        <button @click="viewApps(job.id)" class="btn btn-sm btn-info ms-2">
          View Applications
        </button>
      </li>
    </ul>

    <hr />

    <ul>
      <li v-for="app in applications" :key="app.application_id">
        Student {{ app.student_id }} - {{ app.status }}

        <button @click="updateStatus(app.application_id, 'shortlisted')" class="btn btn-sm btn-warning">
          Shortlist
        </button>

        <button @click="updateStatus(app.application_id, 'selected')" class="btn btn-sm btn-success">
          Select
        </button>
      </li>
    </ul>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      title: '',
      cgpa: '',
      jobs: [],
      applications: []
    }
  },
  methods: {
    async createJob() {
      await axios.post('http://127.0.0.1:5000/api/company/create-job', {
        title: this.title,
        cgpa_required: this.cgpa
      }, {
        headers: {
          Authorization: "Bearer " + localStorage.getItem("token")
        }
      })

      alert("Job created")
    },

    async loadJobs() {
      const res = await axios.get('http://127.0.0.1:5000/api/company/jobs', {
        headers: {
          Authorization: "Bearer " + localStorage.getItem("token")
        }
      })

      this.jobs = res.data
    },

    async viewApps(jobId) {
      const res = await axios.get(`http://127.0.0.1:5000/api/company/job/${jobId}/applications`, {
        headers: {
          Authorization: "Bearer " + localStorage.getItem("token")
        }
      })

      this.applications = res.data
    },

    async updateStatus(id, status) {
      await axios.put(`http://127.0.0.1:5000/api/company/application/${id}/update`, {
        status: status
      }, {
        headers: {
          Authorization: "Bearer " + localStorage.getItem("token")
        }
      })

      alert("Updated")
    }
  }
}
</script>