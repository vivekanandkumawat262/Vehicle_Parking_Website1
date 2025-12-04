 <template>
  <div class="container">
    <h3 class="text-center mb-4">Select a Spot (Lot {{ lotId }})</h3>

    <div class="d-flex flex-wrap gap-3 justify-content-center">

      <div v-for="s in spots" :key="s.id" class="spot-card">

        <button 
          class="btn"
          :disabled="s.status !== 'A'"
          @click="goToBook(s.id)"
        >
          Spot {{ s.id }}
          <br/>
          <span v-if="s.status === 'A'" class="text-success">Available</span>
          <span v-else class="text-danger">Occupied</span>
        </button>

      </div>

    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      lotId: null,
      spots: []
    };
  },

  async created() {
    this.lotId = this.$route.params.lotId;
    const token = localStorage.getItem("token");

    const res = await axios.get(
      `http://127.0.0.1:5000/user/parkinglots/${this.lotId}/spots`,
      { headers: { Authorization: `Bearer ${token}` } }
    );

    this.spots = res.data.spots;
  },

  methods: {
    goToBook(spotId) {
      this.$router.push(`/user/book/${this.lotId}/${spotId}`);
    }
  }
};
</script>
