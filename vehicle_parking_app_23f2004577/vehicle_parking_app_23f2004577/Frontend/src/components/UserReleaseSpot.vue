<template>
  <div class="booking-container">
    <h3 class="header">Release the parking spot</h3>

    <form class="form-box" @submit.prevent="confirmRelease">

      <div class="row-box">
        <label>Spot_ID :</label>
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
        <button class="reserve-btn" type="submit">Release</button>
        <button class="cancel-btn" type="button" @click="cancelRelease">Cancel</button>
      </div>

    </form>
  </div>
</template>

<script>
import axios from "axios"

export default {
  data() {
    return {
      reservationId: null,
      spotId: "",
      vehicleNo: "",
      parkingTime: "",
      releasingTime: "",
      totalCost: "",
      token: ""
    }
  },

  async created() {
    this.reservationId = this.$route.params.reservationId
    this.token = localStorage.getItem("token")

    // Call API to get pre-filled data
    const res = await axios.post(
      "http://127.0.0.1:5000/api/release",
      { reservation_id: this.reservationId },
      {
        headers: { Authorization: `Bearer ${this.token}` }
      }
    )

    const data = res.data
    this.spotId = data.spot_id
    this.vehicleNo = data.vehicle_no
    this.parkingTime = data.parking_time
    this.releasingTime = data.releasing_time
    this.totalCost = data.total_cost
  },

  methods: {
    confirmRelease() {
      alert("Spot successfully released!")
      this.$router.push("/dashboard")
    },

    cancelRelease() {
      this.$router.push("/dashboard")
    }
  }
}
</script>

<style scoped>
/* same styles as booking component */
</style>
