<template>
  <div class="booking-container">
    <h3 class="header">Release the parking spot</h3>

    <form class="form-box" @submit.prevent="confirmRelease">
      <div class="row-box">
        <label>Spot ID :</label>
        <input type="text" :value="spotId" disabled />
      </div>

      <div class="row-box">
        <label>Vehicle Number :</label>
        <input type="text" :value="vehicleNo" disabled />
      </div>

      <div class="row-box">
        <label>Parking Time :</label>
        <input type="text" :value="parkingTime" disabled />
      </div>

      <div class="row-box">
        <label>Releasing Time :</label>
        <input type="text" :value="releasingTime" disabled />
      </div>

      <div class="row-box">
        <label>Total Cost :</label>
        <input type="text" :value="totalCost" disabled />
      </div>

      <div class="btn-row">
        <button class="reserve-btn" type="submit" :disabled="loading">
          {{ loading ? "Releasing..." : "Release" }}
        </button>
      </div>
    </form>

    <button class="cancel-btn" type="button" @click="cancelRelease">
      Cancel
    </button>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "ReleaseSpot",

  data() {
    return {
      reservationId: null,
      spotId: "",
      vehicleNo: "",
      parkingTime: "",
      releasingTime: "",
      totalCost: "",
      token: "",
      loading: false
    };
  },

  async created() {
    try {
      this.reservationId = this.$route.params.reservationId;
      this.token = localStorage.getItem("token");

      if (!this.reservationId) {
        alert("No reservation ID found.");
        this.$router.push("/dashboard");
        return;
      }

      // 🔹 Prefill data WITHOUT releasing the spot
      const res = await axios.get(
        `http://127.0.0.1:5000/api/reservation/${this.reservationId}`,
        {
          headers: { Authorization: `Bearer ${this.token}` }
        }
      );

      const data = res.data;
      this.spotId = data.spot_id;
      this.vehicleNo = data.vehicle_no;
      this.parkingTime = data.parking_time;
      this.releasingTime = data.releasing_time || ""; // might be null before release
      this.totalCost = data.price_per_hour || "";       // might be 0 before release
    } catch (err) {
      console.error(err);
      alert("Failed to load reservation details.");
      this.$router.push("/dashboard");
    }
  },

  methods: {
    async confirmRelease() {
      try {
        this.loading = true;

        const res = await axios.post(
          "http://127.0.0.1:5000/api/release",
          { reservation_id: this.reservationId },
          {
            headers: { Authorization: `Bearer ${this.token}` }
          }
        );

        const data = res.data;

        // 🔹 Update UI with final released values
        this.spotId = data.spot_id;
        this.vehicleNo = data.vehicle_no;
        this.parkingTime = data.parking_time;
        this.releasingTime = data.releasing_time;
        this.totalCost = data.total_cost;

        alert("Spot successfully released!");
        this.$router.push("/dashboard");
      } catch (err) {
        console.error(err);
        const msg =
          err.response?.data?.error ||
          err.response?.data?.message ||
          "Failed to release spot.";
        alert(msg);
      } finally {
        this.loading = false;
      }
    },

    cancelRelease() {
      this.$router.push("/dashboard");
    }
  }
};
</script>

<style scoped>
.booking-container {
  max-width: 500px;
  margin: 2rem auto;
  padding: 1.5rem;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header {
  text-align: center;
  margin-bottom: 1.5rem;
}

.form-box {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.row-box {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.row-box label {
  font-weight: 600;
}

.row-box input {
  padding: 0.4rem 0.6rem;
  border-radius: 4px;
  border: 1px solid #ccc;
}

.btn-row {
  margin-top: 1rem;
  text-align: center;
}

.reserve-btn {
  padding: 0.5rem 1.5rem;
  border-radius: 20px;
  border: none;
  background-color: #007bff;
  color: #fff;
  cursor: pointer;
}

.reserve-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.cancel-btn {
  margin-top: 0.75rem;
  display: block;
  margin-left: auto;
  margin-right: auto;
  padding: 0.4rem 1.2rem;
  border-radius: 20px;
  border: 1px solid #ccc;
  background-color: #f8f9fa;
  cursor: pointer;
}
</style>
