<template>
  <div id="app">
    <nav class="nav">
      <div class="nav-links">
        <router-link to="/">Home</router-link>
        <router-link to="/about">About</router-link>
        <router-link to="/call-records">Call Records</router-link>
        <router-link to="/phone-lookup">Phone Lookup</router-link>
        <router-link to="/port-status">Port Status</router-link>
      </div>
      <button @click="refresh" class="refresh-button" :disabled="isLoading">
        {{ isLoading ? 'Loading...' : 'Refresh' }}
      </button>
    </nav>
    <router-view />
  </div>
</template>

<script setup>
import { ref, provide } from 'vue';

const isLoading = ref(false);
const refresh = () => {
  isLoading.value = true;
  // Notify child components to refresh
  refreshCallback?.();
};

let refreshCallback = null;
provide('setRefreshCallback', (callback) => {
  refreshCallback = callback;
});

provide('setLoading', (loading) => {
  isLoading.value = loading;
});
</script>

<style scoped>
.nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background-color: white;
  padding: 10px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.nav-links {
  display: flex;
  gap: 12px;
}

.nav a.router-link-active {
  font-weight: 600;
}

.refresh-button {
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.refresh-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

#app {
  padding-top: 60px; /* Adjust for the fixed nav height */
}
</style>
