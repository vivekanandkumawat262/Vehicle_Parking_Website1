<template>
  <div class="profile-container">

    <h2 class="title">Edit Profile</h2>

    <div class="profile-box">
      <form @submit.prevent="updateProfile">

        <div class="form-group">
          <label>Username</label>
          <input type="text" v-model="form.username" required />
        </div>

        <div class="form-group">
          <label>Email</label>
          <input type="email" v-model="form.email" required />
        </div>

        <div class="form-group">
          <label>New Password (optional)</label>
          <input type="password" v-model="form.password" placeholder="Leave empty to keep old password" />
        </div>

        <div class="btn-row">
          <button type="submit" class="save-btn">Save Changes</button>
          <button type="button" class="cancel-btn" @click="goBack">Cancel</button>
        </div>

      </form>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      token: "",
      form: {
        username: "",
        email: "",
        password: ""
      }
    }
  },

  async created() {
    this.token = localStorage.getItem("token");

    const res = await axios.get("http://127.0.0.1:5000/user/profile", {
      headers: { Authorization: `Bearer ${this.token}` }
    });

    this.form.username = res.data.username;
    this.form.email = res.data.email;
  },

  methods: {
    async updateProfile() {
      try {
        const res = await axios.put(
          "http://127.0.0.1:5000/user/profile",
          this.form,
          {
            headers: { Authorization: `Bearer ${this.token}` }
          }
        );

        alert("Profile updated!");
        this.$router.push("/dashboard");

      } catch (err) {
        alert("Update failed.");
      }
    },

    goBack() {
      this.$router.push("/dashboard");
    }
  }
};
</script>

<style scoped>
.profile-container {
  width: 450px;
  margin: 40px auto;
}

.title {
  text-align: center;
  margin-bottom: 20px;
}

.profile-box {
  background: #f9f9f9;
  padding: 25px;
  border-radius: 10px;
  border: 2px solid #ddd;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  font-weight: bold;
  display: block;
  margin-bottom: 5px;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border-radius: 6px;
  border: 1px solid #bbb;
}

.btn-row {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.save-btn {
  background: #4dabff;
  color: white;
  border: none;
  padding: 10px 20px;
  font-weight: bold;
  border-radius: 6px;
  cursor: pointer;
}

.cancel-btn {
  background: #ccc;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
}
</style>
