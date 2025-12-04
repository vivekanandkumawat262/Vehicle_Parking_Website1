<template>
  <div class="container mt-5">
    <div class="card shadow-lg p-4 rounded-4">
      <h3 class="text-center mb-4">Admin Profile</h3>

      <div v-if="profile">
        <div class="mb-3">
          <label class="form-label fw-bold">Username</label>
          <input v-model="profile.username" class="form-control" disabled />
        </div>

        <div class="mb-3">
          <label class="form-label fw-bold">Email</label>
          <input v-model="profile.email" class="form-control" />
        </div>

        <div class="mb-3">
          <label class="form-label fw-bold">Change Password</label>
          <input
            v-model="profile.password"
            type="password"
            class="form-control"
            placeholder="Leave blank to keep old password"
          />
        </div>

        <button class="btn btn-primary w-100" @click="updateProfile">
          Save Changes
        </button>
      </div>

      <div v-else class="text-center mt-3 text-muted">Loading...</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { useRouter } from "vue-router"; // ✅ import router
const router = useRouter(); // ✅ define router


const profile = ref(null);

const fetchProfile = async () => {
  try {
    const token = localStorage.getItem("token"); // get the saved JWT

    const response = await axios.get("http://localhost:5000/admin/profile", {
      headers: {
        Authorization: `Bearer ${token}`, // ✅ include JWT here
      },
      withCredentials: true, // optional if your Flask-JWT setup uses cookies
    });
    console.log("hello")
    console.log(response.data)
    profile.value = response.data;
  } catch (error) {
    console.error("Error fetching profile:", error);
    if (error.response && error.response.status === 401) {
      alert("Unauthorized: Please log in again.");
    }
  }
};

const updateProfile = async () => {
  try {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("⚠️ You are not logged in. Please log in again.");
      return;
    }

    const payload = {
      username: profile.value.username, // Include name too
      email: profile.value.email,
      password: profile.value.password || "", // Optional if you allow password update
    };

    const response = await axios.put(
      "http://localhost:5000/admin/profile",
      payload,
      {
        headers: {
          Authorization: `Bearer ${token}`, // ✅ JWT header
          "Content-Type": "application/json",
        },
        withCredentials: true, // Optional for cookies
      }
    );
    console.log("hello")
    console.log(payload)
    // Handle backend success
    if (response.status === 200) {
      alert("✅ Profile updated successfully!");
      profile.value.password = ""; // clear password after update
      router.push("/dashboard"); // ✅ Correct redirect
    }
  } catch (error) {
    console.error("Error updating profile:", error);

    if (error.response) {
      if (error.response.status === 401) {
        alert("⚠️ Unauthorized. Please log in again.");
      } else if (error.response.status === 400) {
        alert("❌ Invalid input. Please check your details.");
      } else {
        alert(`❌ Failed to update profile: ${error.response.data.msg || "Unknown error"}`);
      }
    } else {
      alert("❌ Network error. Please check your connection.");
    }
  }
};


onMounted(fetchProfile);
</script>
