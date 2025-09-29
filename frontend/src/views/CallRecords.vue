<template>
  <main>
    <h1>Call Records</h1>

    <section id="status" aria-live="polite">{{ status }}</section>

    <section>
      <div class="controls">
        <label>Search: <input v-model="q" @keyup.enter="loadRecords" placeholder="phone number or caller" /></label>
        <button @click="loadRecords">Search</button>
      </div>

      <table class="records">
        <thead>
          <tr>
            <th>Date</th>
            <th>Caller</th>
            <th>Original DNIS</th>
            <th>PBX translate</th>
            <th>Secs</th>
            <th>CS # (by CID)</th>
            <th>Usage</th>
            <th>Notes</th>
            <th>Port Date</th>
            <th>Order #</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="records.length === 0"><td colspan="5">No records</td></tr>
          <tr v-for="r in records" :key="r.id">
            <td>{{ fmtDate(r.calldate) }}</td>
            <td>{{ fmtNumber(r.caller) }}</td>
            <td>{{ r.orig_dnis }}</td>
            <td>{{ r.callee !== r.orig_dnis ? fmtNumber(r.callee) : '-same-' }}</td>
            <td>{{ r.duration || '-' }}</td>
            <td :class="{'highlight': !highlight(r)}">{{ r.cs_no || '-' }} <span v-if="r.cs_no_rows">[ {{ r.cs_no_rows  }} others]</span></td>
            <td>{{ r.lumen_usage || '-' }}</td>
            <td>{{ r.lumen_notes || '-' }}</td>
            <td>{{ r.lumen_port_date || '-' }}</td>
            <td>{{ r.lumen_order_num || '-' }}</td>
          </tr>
        </tbody>
      </table>

      <div class="pager">
        <button @click="prevPage" :disabled="page <= 1">Prev</button>
        <span>Page {{ page }}</span>
        <button @click="nextPage">Next</button>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref } from 'vue'

const baseUrl = (window.__API_BASE__ && window.__API_BASE__) || 'http://127.0.0.1:8000'

const status = ref('')
const records = ref([])
const q = ref('')
const page = ref(1)
const pageSize = 25

function showStatus(msg = '') { status.value = msg }

function fmtNumber(v) {
  if (!v) return ''
  const s = String(v)
  // if (s.length === 10) return `(${s.slice(0,3)}) ${s.slice(3,6)}-${s.slice(6)}`
  if (s.length === 12 && s[0] === '+') return `${s.slice(2,12)}`
  return s
}

function highlight(r) {
  if (r.cs_no && r.lumen_usage) {
    var prefix = r.cs_no.slice(0, -4);
    if (r.lumen_usage.indexOf(prefix) !== -1) {
      return true;
    }
  }
  return false;

}

function fmtDate(iso) {
  if (!iso) return ''
  try { return new Date(iso).toLocaleString() } catch (e) { return iso }
}

async function loadRecords() {
  showStatus('Loading...')
  try {
    const params = new URLSearchParams()
    params.set('q', q.value || '')
    params.set('page', String(page.value))
    params.set('page_size', String(pageSize))
    const res = await fetch(`${baseUrl}/call_records?` + params.toString())
    if (!res.ok) throw new Error(`Failed: ${res.status}`)
    records.value = await res.json()
    showStatus('')
  } catch (err) {
    showStatus('Could not load call records — is the API running?')
    console.error(err)
  }
}

function nextPage() { page.value++; loadRecords() }
function prevPage() { if (page.value > 1) { page.value--; loadRecords() } }

// initial load
loadRecords()
</script>

<style>
.controls { margin-bottom: 12px }
.records { width: 100%; border-collapse: collapse }
.records th, .records td { border: 1px solid #ddd; padding: 6px }
.pager { margin-top: 12px }
.highlight { background-color: yellow; font-weight: bold; }
</style>
