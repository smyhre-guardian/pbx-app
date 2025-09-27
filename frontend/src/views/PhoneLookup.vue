<template>
  <div class="phone-lookup">
    <h1>Phone Lookup (DW)</h1>
    <form @submit.prevent="doLookup">
      <input v-model="phone" placeholder="Enter phone number" />
      <button type="submit">Lookup</button>
    </form>
    <div v-if="loading">Loading...</div>
    <div v-if="error" class="error">{{ error }}</div>
    <table v-if="results.length">
      <thead>
        <tr>
          <th>CS No</th>
          <th>Count</th>
          <th>Phone</th>
          <th>First</th>
          <th>Latest</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in results" :key="row.cs_no + row.phone">
          <td>{{ row.cs_no }}</td>
          <td>{{ row.cnt }}</td>
          <td>{{ row.phone }}</td>
          <td>{{ row.first_day }}</td>
          <td>{{ row.last_day }}</td>
        </tr>
      </tbody>
    </table>
    <div v-else-if="!loading">No results found.</div>
  </div>
</template>

<script>
const baseUrl = (window.__API_BASE__ && window.__API_BASE__) || 'http://127.0.0.1:8000'

export default {
  name: "PhoneLookup",
  data() {
    return {
      phone: "",
      results: [],
      loading: false,
      error: ""
    };
  },
  methods: {
    async doLookup() {
      this.loading = true;
      this.error = "";
      this.results = [];
      try {
        const resp = await fetch(`${baseUrl}/phone_lookup?phone=${encodeURIComponent(this.phone)}`);
        if (!resp.ok) throw new Error("API error: " + resp.status);
        this.results = await resp.json();
      } catch (e) {
        this.error = e.message;
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.phone-lookup {
  max-width: 600px;
  margin: 2em auto;
}
input {
  padding: 0.5em;
  margin-right: 1em;
}
button {
  padding: 0.5em 1em;
}
table {
  margin-top: 2em;
  width: 100%;
  border-collapse: collapse;
}
th, td {
  border: 1px solid #ccc;
  padding: 0.5em;
}
.error {
  color: red;
  margin-top: 1em;
}
</style>
