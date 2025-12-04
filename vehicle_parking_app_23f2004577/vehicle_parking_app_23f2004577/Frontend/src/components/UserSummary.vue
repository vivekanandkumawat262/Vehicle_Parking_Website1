<template>
  <div class="summary-container">

    <div class="header-box">
      <span>Welcome, {{ userName }}</span>

      <span class="menu">
        <RouterLink to="/dashboard">Home</RouterLink> |
        <RouterLink to="/user/summary">Summary</RouterLink> |
        <a href="#" @click="logout">Logout</a>
      </span>

      <button class="profile-btn" @click="editProfile">
        Edit Profile
      </button>
    </div>

    <div class="chart-box">
      <canvas id="userSummaryChart"></canvas>
      <p class="caption">Summary on already used parking spots</p>
    </div>

  </div>
</template>

<script>
import axios from "axios";
import { Chart } from "chart.js/auto";

export default {
  data() {
    return {
      userName: "",
      token: "",
      summaryData: []
    };
  },

  async mounted() {
    this.token = localStorage.getItem("token");

    // Fetch user data for name
    const dashboard = await axios.get("http://127.0.0.1:5000/api/dashboard", {
      headers: { Authorization: `Bearer ${this.token}` }
    });
    this.userName = dashboard.data.username;

    // Fetch summary
    const res = await axios.get("http://127.0.0.1:5000/user/summary", {
      headers: { Authorization: `Bearer ${this.token}` }
    });

    this.summaryData = res.data;

    this.renderChart();
  },

  methods: {
    renderChart() {
      const labels = this.summaryData.map(a => a.location);
      const values = this.summaryData.map(a => a.count);

      new Chart(document.getElementById("userSummaryChart"), {
        type: "bar",
        data: {
          labels: labels,
          datasets: [{
            label: "Parking Usage Count",
            data: values,
            backgroundColor: ["#7dd87d", "#74b9ff", "#ff7675"]
          }]
        },
        options: {
          responsive: true,
          scales: { y: { beginAtZero: true } }
        }
      });
    },

    editProfile() {
      this.$router.push("/user/profile");
    },

    logout() {
      localStorage.removeItem("token");
      this.$router.push("/login");
    }
  }
}
</script>

<style scoped>
.summary-container {
  width: 90%;
  margin: auto;
  margin-top: 20px;
}

.header-box {
  background: #b6f7b6;
  padding: 12px;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
}

.profile-btn {
  border: none;
  background: #4dabff;
  padding: 8px 16px;
  border-radius: 6px;
  color: white;
}

.chart-box {
  width: 500px;
  margin: 40px auto;
  text-align: center;
}

.caption {
  font-size: 14px;
  margin-top: 8px;
}
</style>
