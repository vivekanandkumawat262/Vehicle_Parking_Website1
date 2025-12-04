<template>
  <div class="container mt-4">
    <h4 class="text-center text-primary mb-4">
      Parking Lot #{{ lotId }} — Spot #{{ spotId }}
    </h4>

    <div v-if="spot">
      <div
        class="spot-box mx-auto"
        :class="{
          available: spot.spot_status === 'A',
          occupied: spot.spot_status === 'O',
          reserved: spot.spot_status === 'R'
        }"
        @click="openModal"
      >
        {{ spot.spot_id }}
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-content">
        <h5 class="text-center mb-3">View / Delete Parking Spot</h5>
        <p><strong>Lot Name:</strong> {{ spot.prime_location_name }}</p>
        <p><strong>Spot ID:</strong> {{ spot.spot_id }}</p>
        <p><strong>Status:</strong> {{ spot.spot_status }}</p>
        <p><strong>Price:</strong> ₹{{ spot.price }}</p>

        <div class="text-center mt-4">
          <button
            class="btn btn-danger me-2"
            :disabled="spot.spot_status === 'O'"
            @click="deleteSpot"
          >
            Delete
          </button>
          <button class="btn btn-secondary" @click="closeModal">Close</button>
        </div>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger text-center mt-3">
      {{ error }}
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      lotId: null,
      spotId: null,
      spot: null,
      showModal: false,
      error: null,
    };
  },

  async mounted() {
    this.lotId = this.$route.params.lot_id;
    this.spotId = this.$route.params.spot_id;
    await this.getSpotDetails();
  },

  methods: {
    // ✅ Fetch specific parking spot by lot_id & spot_id
    async getSpotDetails() {
      try {
        const token = localStorage.getItem("token");
        const res = await fetch(
          `http://127.0.0.1:5000/api/parkinglot/${this.lotId}/${this.spotId}`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        if (!res.ok) throw new Error(`Failed to fetch spot: ${res.status}`);
        this.spot = await res.json();
        console.log("Fetched spot:", this.spot);
      } catch (err) {
        this.error = err.message;
      }
    },

    openModal() {
      this.showModal = true;
    },

    closeModal() {
      this.showModal = false;
    },

    // ✅ Delete the selected spot (same URL structure)
    async deleteSpot() {
      try {
        const token = localStorage.getItem("token");
        const res = await fetch(
          `http://127.0.0.1:5000/api/delete-spot/${this.lotId}/${this.spotId}`,
          {
            method: "DELETE",
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Failed to delete spot");

        alert("Spot deleted successfully!");
        this.showModal = false;

        // Redirect after deletion
        this.$router.push("/dashboard");
      } catch (err) {
        alert(err.message);
      }
    },
  },
};
</script>

<style scoped>
.spot-box {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  color: white;
  font-weight: bold;
  cursor: pointer;
  font-size: 1.2em;
}

.available {
  background-color: green;
}
.occupied {
  background-color: red;
}
.reserved {
  background-color: orange;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 10px;
  width: 350px;
}

.alert {
  width: 80%;
  margin: auto;
}
</style>
