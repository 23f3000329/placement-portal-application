<!-- src/views/Login.vue -->
<template>
  <div class="container mt-5">
    <h2>Login</h2>

    <input v-model="email" placeholder="Email" class="form-control mb-2" />
    <input v-model="password" type="password" placeholder="Password" class="form-control mb-2" />

    <button @click="login" class="btn btn-primary">Login</button>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      email: '',
      password: ''
    }
  },
  methods: {
    async login() {
      try {
        const res = await axios.post('http://127.0.0.1:5000/api/auth/login', {
          email: this.email,
          password: this.password
        })

        localStorage.setItem("token", res.data.token)
        localStorage.setItem("role", res.data.role)

        if (res.data.role === "admin") this.$router.push('/admin')
        else if (res.data.role === "company") this.$router.push('/company')
        else this.$router.push('/student')

      } catch (err) {
        alert("Login failed")
      }
    }
  }
}
</script>