<template>
  <main>
    <h1>About</h1>
    <p>
      <button @click="pull()">Pull code from git</button>
    </p>
  </main>
</template>

<script setup>
import { ref } from 'vue'
const pull = async () => {
  try {
    const res = await fetch((import.meta.env.VITE_API_URL || 'http://localhost:8000') + '/git-pull');
    const data = await res.json();
    alert('Git Pull Result:\n' + JSON.stringify(data, null, 2));
  } catch (e) {
    alert('Error during git pull: ' + e.message);
  }
}
</script>

<style>
main { max-width: 1000px; margin: 0 auto; background: white; padding: 18px; border-radius: 8px; }
</style>
