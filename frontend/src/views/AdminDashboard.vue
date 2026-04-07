<template>
  <div class="container mt-5">
    <h2>Admin Dashboard</h2>

    <button @click="loadCompanies" class="btn btn-primary mb-3">
      Load Companies
    </button>

    <ul>
      <li v-for="c in companies" :key="c.id">
        {{ c.name }} - {{ c.approved }}
      </li>
    </ul>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      companies: []
    }
  },
  methods: {
    async loadCompanies() {
      const res = await axios.get('http://127.0.0.1:5000/api/admin/companies', {
        headers: {
          Authorization: "Bearer " + localStorage.getItem("token")
        }
      })

      this.companies = res.data
    }
  }
}
</script>