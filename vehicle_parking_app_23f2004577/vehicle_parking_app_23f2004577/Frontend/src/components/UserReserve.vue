<template>
  <div class="booking-container">
    <h3 class="header">Book the parking spot</h3>

    <form class="form-box" @submit.prevent="confirmBooking">

      <!-- Spot ID (pre-filled) -->
      <div class="row-box">
        <label>Spot_ID :</label>
        <input type="text" :value="spotId" disabled />
      </div>

      <!-- Lot ID (pre-filled) -->
      <div class="row-box">
        <label>Lot_ID :</label>
        <input type="text" :value="lotId" disabled />
      </div>

      <!-- User ID (pre-filled) -->
      <div class="row-box">
        <label>User ID :</label>
        <input type="text" :value="userId" disabled />
      </div>

      <!-- Vehicle Number (user entry) -->
      <div class="row-box">
        <label>Vehicle Number :</label>
        <input 
          type="text" 
          v-model="vehicleNumber"
          placeholder="Enter vehicle number"
          required
        />
      </div>

      <!-- Buttons -->
      <div class="btn-row">
        <button class="reserve-btn" type="submit">Reserve</button>
        <button class="cancel-btn" type="button" @click="cancelBooking">Cancel</button>
      </div>

    </form>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      lotId: null,
      spotId: null,
      userId: null,
      vehicleNumber: "",
      token: "",
    };
  },

  created() {
    this.lotId = this.$route.params.lotId;
    this.spotId = this.$route.params.spotId;
    this.token = localStorage.getItem("token");

    // Decode userId from token or store it from dashboard 
    const userData = JSON.parse(localStorage.getItem("userData"));
    console.log(userData?.role);
    console.log("Local storage userData:", userData);

    this.userId = userData?.id;
    console.log("User ID:", this.userId);
     

  },

  methods: {
    async confirmBooking() {
      try {
        const res = await axios.post(
          "http://127.0.0.1:5000/api/reserve",
          {
            user_id: this.userId,
            lot_id: this.lotId,
            spot_id: this.spotId,
            vehicle_no: this.vehicleNumber,
          },
          {
            headers: { Authorization: `Bearer ${this.token}` },
          }
        );

        alert("Spot reserved successfully!");
        this.$router.push("/dashboard");

      } catch (err) {
        alert("Failed to reserve spot.");
      }
    },

    cancelBooking() {
      this.$router.push("/dashboard");
    },
  },
};
</script>

<style scoped>
.booking-container {
  width: 420px;
  margin: 30px auto;
  padding: 20px;
  background: #fff7d1;
  border-radius: 12px;
  border: 2px solid #e4c86f;
  box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
}

.header {
  text-align: center;
  background: #ffe998;
  padding: 12px;
  border-radius: 8px;
  font-weight: bold;
  font-size: 20px;
  margin-bottom: 20px;
}

.form-box {
  padding: 10px 5px;
}

.row-box {
  margin-bottom: 15px;
}

.row-box label {
  display: block;
  font-weight: bold;
  margin-bottom: 4px;
}

.row-box input {
  width: 100%;
  padding: 8px;
  border-radius: 6px;
  border: 1px solid #aaa;
}

.btn-row {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.reserve-btn {
  background: #4dabff;
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  font-weight: bold;
  cursor: pointer;
}

.cancel-btn {
  background: #eaeaea;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: bold;
  border: none;
  cursor: pointer;
}
</style>
