<template>
  <main>
    <h1>Upload Excel File</h1>
    <form @submit.prevent="uploadFile">
      <input type="file" @change="handleFileChange" accept=".xlsx, .xls" />
      <button type="submit">Upload</button>
    </form>
    <div v-if="data">
      <h2>Parsed Data</h2>
      <h3>Showing {{ changed.length }} changes (new or modified)</h3>
      <table border="1" style="width: 100%; border-collapse: collapse; margin-top: 20px;">
        <thead>
          <tr>
            <!-- <th v-for="(value, key) in data[0]" :key="key">{{ key }}</th> -->
             <td>TN</td>
             <td>Ring-To #</td>
             <td>Usage</td>
             <td>DNIS</td>
             <td>Port Date</td>
             <th>Status</th>
             <td>Order #</td>
             <td>Notes</td>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, rowIndex) in changed" :key="rowIndex">
            <!-- <td v-for="(value, key) in row" :key="key">{{ value }}</td> -->
             <td>{{ row["TN"] }}</td>
             <td v-for="key in ['ring_to', 'usage', 'DNIS', 'port_date', 'status', 'order_num', 'notes']">
                <span v-if="row.differences[key] !== undefined">
                    <span class="before">{{  row.differences[key].old }}</span> -&gt; <span class="after">{{  row.differences[key].new }}</span>
                </span>
                <span v-else-if="row.existing && row.existing[key] !== undefined">{{  row.existing[key] }}</span>
             </td>
          </tr>
        </tbody>
    </table>
    </div>
  </main>
</template>

<script setup>
import { ref, computed } from 'vue';

const file = ref(null);
const data = ref(null);
const changed = computed(() => {
  if (!data.value) return [];
  return data.value.filter(row => row.is_new || (row.differences && Object.keys(row.differences).length > 0));
});
const handleFileChange = (event) => {
  file.value = event.target.files[0];
};

const uploadFile = async () => {
  if (!file.value) {
    alert('Please select a file first.');
    return;
  }

  const formData = new FormData();
  formData.append('file', file.value);

  try {
    const res = await fetch((import.meta.env.VITE_API_URL || 'http://localhost:8000') + '/upload-excel', {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      throw new Error('Failed to upload file');
    }

    const result = await res.json();
    data.value = result.data;
  } catch (error) {
    alert('Error uploading file: ' + error.message);
  }
};
</script>

<style>
main {
  max-width: 1400px;
  margin: 0 auto;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
button {
  padding: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
button:hover {
  background-color: #0056b3;
}
.after {
    background-color: #d4f8d4;
}
.before {
    background-color: #f8d4d4;
}

.before, .after {
    padding: 2px 4px;
    border-radius: 4px;
    display: inline-block;
    margin: 3px 5px;
}
</style>