<template>
  <footer class="bg-dark text-light py-4 mt-auto">
    <div class="container text-center">
      <div class="row">
        <!-- Left Column -->
        <div class="col-md-4 mb-3 mb-md-0">
          <h5 class="fw-bold text-uppercase">Vehicle Parking System</h5>
          <p class="small mb-0">
            Smart and efficient parking management made simple.
          </p>
        </div>

        <!-- Middle Column -->
        <div class="col-md-4 mb-3 mb-md-0">
          <h6 class="fw-bold text-uppercase">Quick Links</h6>
          <ul class="list-unstyled">
            <li><RouterLink to="/" class="text-light text-decoration-none">Home</RouterLink></li>
            <li><RouterLink to="/login" class="text-light text-decoration-none">Login</RouterLink></li>
            <li><RouterLink to="/about" class="text-light text-decoration-none">About</RouterLink></li>
            <li><RouterLink to="/contact" class="text-light text-decoration-none">Contact</RouterLink></li>
          </ul>
        </div>

        <!-- Right Column -->
        <div class="col-md-4">
          <h6 class="fw-bold text-uppercase">Connect With Us</h6>
          <a href="#" class="text-light me-3"><i class="bi bi-facebook fs-5"></i></a>
          <a href="#" class="text-light me-3"><i class="bi bi-twitter fs-5"></i></a>
          <a href="#" class="text-light me-3"><i class="bi bi-instagram fs-5"></i></a>
          <a href="#" class="text-light"><i class="bi bi-envelope fs-5"></i></a>
        </div>
      </div>

      <hr class="border-secondary my-3" />

      <p class="mb-0 small">&copy; {{ new Date().getFullYear() }} Vehicle Parking System. All rights reserved.</p>
    </div>
  </footer>
</template>

<script>
export default {
  name: "Footer",
};
</script>

<style scoped>
footer {
  position: relative;
  bottom: 0;
  width: 100%;
}
</style>
