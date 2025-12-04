<template>
  <div class="search-container">
    <!-- 🔍 Search Section -->
    <div class="search-bar mb-3">
      <label class="fw-bold me-2">Search by:</label>
      <select v-model="searchBy" class="form-select d-inline-block w-auto me-2">
        <option value="location">Location</option>
        <option value="id">Parking Lot ID</option>
        <option value="address">Parking Lot Address</option>
      </select>

      <input
        v-model="searchString"
        type="text"
        placeholder="Enter search query..."
        class="form-control d-inline-block w-auto me-2"
      />

      <button class="btn btn-primary" @click="handleAdminSearch">Search</button>
      <button class="btn btn-outline-secondary ms-2" @click="clearSearchAndLoadAll">Reset</button>
    </div>

    <!-- 🧾 Pagination Controls -->
    <div v-if="searchTotal !== null" class="d-flex justify-content-between align-items-center mb-3">
      <div>
        <small>Showing page {{ searchPage }} of {{ searchTotalPages }} ({{ searchTotal }} results)</small>
      </div>
      <div>
        <button
          class="btn btn-sm btn-outline-secondary me-1"
          :disabled="searchPage <= 1"
          @click="changePage(searchPage - 1)"
        >
          Prev
        </button>
        <button
          class="btn btn-sm btn-outline-secondary"
          :disabled="searchPage >= searchTotalPages"
          @click="changePage(searchPage + 1)"
        >
          Next
        </button>
      </div>
    </div>

    <!-- 🏙️ Parking Lot Results -->
    <div v-if="parkingLots.length > 0" class="row">
      <div
        v-for="lot in parkingLots"
        :key="lot.id"
        class="col-md-4 mb-4"
      >
        <div class="card shadow-sm">
          <div class="card-body">
            <h5 class="card-title">🏙 Parking #{{ lot.id }} - {{ lot.prime_location_name }}</h5>
            <p class="text-muted mb-1">📍 Address: {{ lot.address }}</p>
            <p class="text-success mb-1">Occupied: {{ lot.occupied }}/{{ lot.number_of_spots }}</p>
            <p class="text-primary fw-bold mb-0">💰 Price: ₹{{ lot.price }}</p>
          </div>
        </div>
      </div>
    </div>

    <p v-else-if="searchPerformed">No parking lots found.</p>
  </div>
</template>

<script setup>
import { ref } from "vue";
import axios from "axios";

// 📌 State variables
const parkingLots = ref([]);
const searchBy = ref("location");
const searchString = ref("");
const searchPage = ref(1);
const searchPerPage = ref(12);
const searchTotal = ref(null);
const searchTotalPages = ref(null);
const lastSearchParams = ref(null);
const searchPerformed = ref(false);
const error = ref("");

// ⚙️ Methods
async function handleAdminSearch() {
  const by = searchBy.value.toLowerCase();
  const q = searchString.value.trim();

  if (by !== "id" && q.length < 1) {
    error.value = "Please enter a search term.";
    return;
  }

  searchPage.value = 1;
  lastSearchParams.value = { by, q };
  await performAdminSearch(by, q, searchPage.value);
}

async function performAdminSearch(by, q, page = 1) {
  error.value = "";
  searchPerformed.value = true;

  try {
    const token = localStorage.getItem("token");
    const res = await axios.get("http://127.0.0.1:5000/admin/search", {
      headers: { Authorization: `Bearer ${token}` },
      params: {
        by,
        q,
        page,
        per_page: searchPerPage.value,
      },
    });

    const data = res.data;
    console.log(data)
    parkingLots.value = data.results || [];
    searchPage.value = data.page || 1;
    searchPerPage.value = data.per_page || 12;
    searchTotal.value = data.total || 0;
    searchTotalPages.value = data.total_pages || 0;
  } catch (err) {
    error.value = err.response?.data?.error || "Search failed. Check console.";
    console.error("Search error:", err);
  }
}

async function changePage(newPage) {
  if (!lastSearchParams.value) return;
  searchPage.value = newPage;
  await performAdminSearch(lastSearchParams.value.by, lastSearchParams.value.q, newPage);
}

async function clearSearchAndLoadAll() {
  lastSearchParams.value = null;
  searchString.value = "";
  parkingLots.value = [];
  searchPerformed.value = false;
  searchTotal.value = null;
}
</script>

<style scoped>
.search-bar {
  margin-top: 20px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}
.card {
  border-radius: 12px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}
</style>
