<template>
  <main>
    <h1>PBX Sync</h1>

    <section>
      <button @click="fetchDiff('SVRPBX01')">SVRPBX01</button>
      <button @click="fetchDiff('SVRPBX02')">SVRPBX02</button>
      <button :disabled="diffs.length == 0" @click="applyConfig('SVRPBX01')">Apply SVRPBX01</button>
      <button :disabled="diffs.length == 0" @click="applyConfig('SVRPBX02')">Apply SVRPBX02</button>
    </section>

    <section v-if="diffs.length > 0">
      <h2>Differences ({{ unmatched.length }} changes)</h2>
      <table style="width: 100%; border-collapse: collapse; margin-top: 20px;" border="1">
        <thead>
          <tr>
            <th>Phone</th>
            <th>Old Extension</th>
            <th>New Extension</th>
            <th>Diff</th>
          </tr>
        </thead>
        <tbody>
            <tr v-for="(line, index) in unmatched" :key="index">
                <td><phone-number-dropdown :phone-number="line.phn" :show-port="true"></phone-number-dropdown></td>
                <td>{{ line.left }}</td>
                <td>{{ line.right }}</td>
                <td>
                    <span v-for="x in runDiff(line.left, line.right)" :class="{
                        'added': x.added,
                        'removed': x.removed
                    }">
                        {{ x.value }}
                    </span>
                </td>
            </tr>
        </tbody>
    </table>
    </section>

    <section v-else-if="status">
      <p>{{ status }}</p>
    </section>
  </main>
</template>

<script setup>
import { computed, ref } from 'vue';
import { diffChars, diffLines } from 'diff';
import PhoneNumberDropdown from '../components/PhoneNumberDropdown.vue';

const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const diffs = ref([]);
const status = ref('');

const unmatched = computed(() => {
  return diffs.value.filter(line => !line.is_match && !line.is_new)
});

const runDiff = function(a,b) {
    return diffLines(a,b);
}

async function fetchDiff(server) {
  status.value = `Fetching differences for ${server}...`;
  diffs.value = [];

  try {
    const res = await fetch(`${baseUrl}/pbx-diff/${server}`);
    if (!res.ok) {
      throw new Error(`Failed to fetch: ${res.status}`);
    }
    const data = await res.json();
    diffs.value = data;
    status.value = '';
  } catch (err) {
    status.value = `Error fetching differences: ${err.message}`;
    console.error(err);
  }
}

async function applyConfig(server) {
  status.value = `Applying configuration for ${server}...`;
  diffs.value = [];

  try {
    const res = await fetch(`${baseUrl}/pbx-sync/${server}`, {
      method: 'POST',
      body: JSON.stringify({}),
    });
    if (!res.ok) {
      throw new Error(`Failed to fetch: ${res.status}`);
    }
    const data = await res.json();
    status.value = data.status;
    status.value += ': ' + data.message;
  } catch (err) {
    status.value = `Error fetching differences: ${err.message}`;
    console.error(err);
  }
}
</script>

<style>
main {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  padding: 18px;
  border-radius: 8px;
}
button {
  margin: 8px;
  font-size: 16px;
  cursor: pointer;
}
td {
    text-align: left;
    padding: 1px 5px;
}
.added {
    background-color: #d4f8d4;
}
.removed {
    background-color: #f8d4d4;
}
</style>