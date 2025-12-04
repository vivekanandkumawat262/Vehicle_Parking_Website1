<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light shadow-sm">
    <div class="container-fluid">
      <!-- Logo / Brand -->
      <RouterLink to="/" class="navbar-brand d-flex align-items-center">
        <img
          src="@/assets/parkingimage.png"
          alt="Parking Logo"
          width="40"
          height="40"
          class="me-2 rounded-circle"
        />
        <span class="fw-bold text-dark">Parking System</span>
      </RouterLink>

      <!-- Toggle button (for small screens) -->
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <!-- Navbar Links -->
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li class="nav-item">
            <RouterLink to="/" class="nav-link text-dark">Home</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink to="/about" class="nav-link text-dark">About</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink to="/contact" class="nav-link text-dark">Contact</RouterLink>
          </li>
        </ul>

        <!-- Search Form -->
        <form class="d-flex" role="search" @submit.prevent="onSearch">
          <input
            v-model="query"
            class="form-control me-2"
            type="search"
            placeholder="Search"
            aria-label="Search"
          />
          <button class="btn btn-outline-success" type="submit">Search</button>
        </form>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: "Navbar",
  data() {
    return {
      query: "",
    };
  },
  methods: {
    onSearch() {
      console.log("Searching for:", this.query);
      // You can add route navigation or API call here
    },
  },
};
</script>

<style scoped>
.navbar-brand span {
  font-size: 1.1rem;
}
</style>
