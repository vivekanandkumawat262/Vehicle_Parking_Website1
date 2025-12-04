<template>
  <div class="container mt-4">
    <h3 class="text-center mb-4 text-primary fw-bold">Admin Dashboard Summary</h3>

    <!-- Spot Summary Section -->
    <div class="row text-center mb-5">
      <div class="col-md-4 mb-3">
        <div class="card shadow-sm border-success">
          <div class="card-body">
            <h5 class="card-title text-success">Available Spots</h5>
            <h2>{{ spotSummary.available }}</h2>
          </div>
        </div>
      </div>

      <div class="col-md-4 mb-3">
        <div class="card shadow-sm border-danger">
          <div class="card-body">
            <h5 class="card-title text-danger">Occupied Spots</h5>
            <h2>{{ spotSummary.occupied }}</h2>
          </div>
        </div>
      </div>

      <div class="col-md-4 mb-3">
        <div class="card shadow-sm border-primary">
          <div class="card-body">
            <h5 class="card-title text-primary">Total Spots</h5>
            <h2>{{ spotSummary.total_spots }}</h2>
          </div>
        </div>
      </div>
    </div>

    <!-- Revenue by Lot Section -->
    <h4 class="mb-3 text-secondary">Revenue by Lot</h4>
    <div class="table-responsive">
      <table class="table table-bordered table-hover">
        <thead class="table-dark">
          <tr>
            <th>Lot ID</th>
            <th>Prime Location Name</th>
            <th>Revenue (₹)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="lot in revenueByLot" :key="lot.lot_id">
            <td>{{ lot.lot_id }}</td>
            <td>{{ lot.prime_location_name }}</td>
            <td>{{ lot.revenue.toFixed(2) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div v-if="revenueByLot.length === 0" class="text-center text-muted mt-3">
      No revenue data available.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";

const revenueByLot = ref([]);
const spotSummary = ref({
  available: 0,
  occupied: 0,
  total_spots: 0,
});

// Fetch summary data from backend API
const fetchSummary = async () => {
  try {
    const token = localStorage.getItem("token"); // or sessionStorage
    const response = await axios.get("http://localhost:5000/admin/summary", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    revenueByLot.value = response.data.revenue_by_lot || [];
    spotSummary.value = response.data.spot_summary || {};
    console.log("hello")
  } catch (error) {
    console.error("Error fetching summary:", error);
  }
};

onMounted(fetchSummary);
</script>

<style scoped>
.card {
  border-radius: 12px;
  transition: all 0.3s ease;
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
}
h2 {
  font-weight: bold;
}
.table th, .table td {
  vertical-align: middle;
}
</style>
