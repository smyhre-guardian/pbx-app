<template>
  <div class="phone-lookup">
    <h1>Phone Lookup</h1><small style="display: block; margin-bottom: 10px; color:#777;">Refreshed every 10 minutes</small>
    
    <form @submit.prevent="doLookup">
      <input v-model="phone" style="width: 250px" ref="search" placeholder="Enter phone number (any format)" />
      <button type="submit">Lookup</button>
    </form>
    <div v-if="loading">Loading...</div>
    <div v-if="error" class="error">{{ error }}</div>
    <a v-if="results.length" style="margin-top: 20px;" :href="'/call-records?q=' + phone">
      View CDRs for {{ phone }}
    </a>
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
        <tr v-for="row in results" :key="row.cs_no + row.last_day">
          <td>{{ row.cs_no }}</td>
          <td>{{ row.cnt }}</td>
          <td>{{ row.phone }}</td>
          <td>{{ formatDay(row.first_day) }}</td>
          <td>{{ formatDay(row.last_day) }}</td>
        </tr>
      </tbody>
    </table>
    <div v-else-if="!loading">No results found.</div>
  </div>
</template>

<script>
const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
  mounted() {
    const queryPhone = this.$route.query.phone;
    if (queryPhone) {
      this.phone = queryPhone;
      this.doLookup();
    }
    this.$refs.search.focus();
  },
  methods: {
    async doLookup() {
      this.loading = true;
      this.error = "";
      this.results = [];
      var stripped = this.phone.replace(/\D/g, '');
      stripped = stripped.slice(-10);
      this.phone = stripped;

      // Update the query string with the phone number
      this.$router.push({ path: this.$route.path, query: { phone: stripped } });

      try {
        const resp = await fetch(`${baseUrl}/phone_lookup?phone=${encodeURIComponent(stripped)}`);
        if (!resp.ok) throw new Error("API error: " + resp.status);
        this.results = await resp.json();
      } catch (e) {
        this.error = e.message;
      } finally {
        this.loading = false;
      }
    },
    formatDay(dayStr) {
      if (!dayStr) return "";
      dayStr = dayStr.toString();
      return dayStr.slice(0,4) + '-' + dayStr.slice(4,6) + '-' + dayStr.slice(6,8);
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
