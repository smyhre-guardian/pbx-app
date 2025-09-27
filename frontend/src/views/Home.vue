<template>
  <main>
    <h1>Phone List</h1>

    <section id="status" aria-live="polite">{{ status }}</section>

    <form @submit.prevent="addNumber" class="add-form">
      <label for="number">Phone number</label>
      <input id="number" v-model="form.number" name="number" placeholder="(555) 123-4567 or 5551234567" required />
      <label for="point_to">Point to</label>
      <input id="point_to" v-model="form.point_to" name="point_to" placeholder="Extension or target (optional)" />
      <button type="submit">Add</button>
    </form>

    <section>
      <h2>Numbers</h2>
      <ul id="list">
        <li v-if="items.length === 0" class="empty">No numbers yet</li>
        <li v-for="item in items" :key="item.id" class="item">
          <div class="info">
            <strong>{{ fmtNumber(item.number) }}</strong>
            <span v-if="item.point_to" class="meta">point_to: {{ item.point_to }}</span>
            <span v-if="item.label" class="meta">{{ item.label }}</span>
            <span v-if="item.usage" class="meta">{{ item.usage }}</span>
          </div>
          <div class="actions">
            <button @click="viewItem(item.id)">View</button>
            <button @click="enterEditMode(item)">Edit</button>
            <button class="danger" @click="deleteItem(item.id)">Delete</button>
          </div>
        </li>
      </ul>

      <div v-if="editing" class="editor">
        <h3>Editing</h3>
        <input v-model="editing.number" placeholder="10 digits" />
        <input v-model="editing.point_to" placeholder="point_to" />
        <button @click="saveEdit">Save</button>
        <button @click="cancelEdit">Cancel</button>
      </div>
    </section>
  </main>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'

const baseUrl = (window.__API_BASE__ && window.__API_BASE__) || 'http://127.0.0.1:8000'

const status = ref('')
const items = ref([])
const form = reactive({ number: '', point_to: '' })
const editing = ref(null)

function showStatus(msg = '', isError = false) {
  status.value = msg
  // classes are provided by global CSS, we keep status text only here
}

function fmtNumber(digits) {
  if (!digits || digits.length !== 10) return digits
  return `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`
}

function _formatErrorBody(body, statusCode) {
  if (!body) return `Error: ${statusCode}`
  if (body.detail) {
    const d = body.detail
    if (Array.isArray(d)) {
      return d.map(e => {
        if (e && e.msg) {
          const loc = Array.isArray(e.loc) ? e.loc.join('.') : e.loc
          return loc ? `${loc}: ${e.msg}` : e.msg
        }
        return typeof e === 'string' ? e : JSON.stringify(e)
      }).join('; ')
    }
    if (typeof d === 'string') return d
    return JSON.stringify(d)
  }
  if (typeof body === 'string') return body
  try { return JSON.stringify(body) } catch (e) { return `Error: ${statusCode}` }
}

async function loadList() {
  showStatus('Loading...')
  try {
    const res = await fetch(`${baseUrl}/phone_numbers`)
    if (!res.ok) throw new Error(`Failed to load: ${res.status}`)
    items.value = await res.json()
    showStatus('')
  } catch (err) {
    showStatus('Could not load list — is the API running?')
    console.error(err)
  }
}

function enterEditMode(item) {
  editing.value = { ...item }
}

async function saveEdit() {
  if (!editing.value) return
  const payload = { number: editing.value.number.trim(), point_to: editing.value.point_to?.trim() || undefined }
  try {
    showStatus('Saving...')
    const res = await fetch(`${baseUrl}/phone_numbers/${editing.value.id}`, {
      method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
    })
    if (res.ok) {
      showStatus('Saved')
      editing.value = null
      await loadList()
      return
    }
    const body = await res.json().catch(() => ({}))
    showStatus(_formatErrorBody(body, res.status))
  } catch (err) {
    showStatus('Could not save')
    console.error(err)
  }
}

function cancelEdit() { editing.value = null }

async function viewItem(id) {
  showStatus('Loading item...')
  try {
    const res = await fetch(`${baseUrl}/phone_numbers/${id}`)
    if (res.status === 404) { showStatus('Item not found'); await loadList(); return }
    if (!res.ok) throw new Error(`Status ${res.status}`)
    const item = await res.json()
    alert(`ID: ${item.id}\nNumber: ${fmtNumber(item.number)}\nPoint to: ${item.point_to || ''}\nLabel: ${item.label || ''}\nUsage: ${item.usage || ''}`)
    showStatus('')
  } catch (err) {
    showStatus('Could not fetch item')
    console.error(err)
  }
}

async function deleteItem(id) {
  if (!confirm('Delete this number?')) return
  showStatus('Deleting...')
  try {
    const res = await fetch(`${baseUrl}/phone_numbers/${id}`, { method: 'DELETE' })
    if (res.status === 404) { showStatus('Item not found'); await loadList(); return }
    if (res.status === 204) { showStatus('Deleted'); await loadList(); return }
    throw new Error(`Unexpected status ${res.status}`)
  } catch (err) {
    showStatus('Could not delete item')
    console.error(err)
  }
}

async function addNumber() {
  const value = form.number.trim()
  const pointVal = form.point_to.trim()
  if (!value) return
  showStatus('Adding...')
  try {
    const res = await fetch(`${baseUrl}/phone_numbers`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ number: value, point_to: pointVal || undefined })
    })
    if (res.status === 201) {
      form.number = ''
      form.point_to = ''
      showStatus('Added')
      await loadList()
      return
    }
    const body = await res.json().catch(() => ({}))
    showStatus(_formatErrorBody(body, res.status))
  } catch (err) {
    showStatus('Could not add number')
    console.error(err)
  }
}

onMounted(() => loadList())
</script>

<style>
/* keep local layout tweaks; global styles live in ./style.css (imported by main.js) */
main { max-width: 1000px; margin: 0 auto; background: white; padding: 18px; border-radius: 8px; }
.add-form { display: flex; gap: 8px; align-items: center; margin-bottom: 12px; }
.add-form input[name=number] { width: 200px; }
.editor { margin-top: 12px; }
</style>
