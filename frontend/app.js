const baseUrl = (window.__API_BASE__ && window.__API_BASE__) || "http://127.0.0.1:8000";

function fmtNumber(digits) {
    if (!digits || digits.length !== 10) return digits;
    return `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`;
}

function showStatus(msg, isError = false) {
    const el = document.getElementById('status');
    el.textContent = msg;
    el.className = isError ? 'error' : 'ok';
    if (!msg) el.className = '';
}

function _formatErrorBody(body, status) {
    if (!body) return `Error: ${status}`;
    // common FastAPI validation shape: { detail: [ {loc, msg, type}, ... ] }
    if (body.detail) {
        const d = body.detail;
        if (Array.isArray(d)) {
            // join messages from validation errors
            return d.map(e => {
                if (e && e.msg) {
                    // include location for clarity
                    const loc = Array.isArray(e.loc) ? e.loc.join('.') : e.loc;
                    return loc ? `${loc}: ${e.msg}` : e.msg;
                }
                return typeof e === 'string' ? e : JSON.stringify(e);
            }).join('; ');
        }
        if (typeof d === 'string') return d;
        return JSON.stringify(d);
    }
    // fallback: stringify the whole body if it's an object
    if (typeof body === 'string') return body;
    try {
        return JSON.stringify(body);
    } catch (e) {
        return `Error: ${status}`;
    }
}

async function loadList() {
    showStatus('Loading...');
    try {
        const res = await fetch(`${baseUrl}/phone_numbers`);
        if (!res.ok) throw new Error(`Failed to load: ${res.status}`);
        const data = await res.json();
        renderList(data);
        showStatus('');
    } catch (err) {
        showStatus('Could not load list — is the API running?', true);
        console.error(err);
    }
}

function renderList(items) {
    const ul = document.getElementById('list');
    ul.innerHTML = '';
    if (!items || items.length === 0) {
        ul.innerHTML = '<li class="empty">No numbers yet</li>';
        return;
    }
    items.forEach(item => {
        const li = document.createElement('li');
        li.className = 'item';
        const txt = document.createElement('div');
        txt.className = 'info';
        txt.innerHTML = `<strong>${fmtNumber(item.number)}</strong>` +
            (item.point_to ? ` <span class="meta">point_to: ${item.point_to}</span>` : '') +
            (item.label ? ` <span class="meta">${item.label}</span>` : '') +
            (item.usage ? ` <span class="meta">${item.usage}</span>` : '');

        const actions = document.createElement('div');
        actions.className = 'actions';

        const viewBtn = document.createElement('button');
        viewBtn.textContent = 'View';
        viewBtn.addEventListener('click', () => viewItem(item.id));

        const delBtn = document.createElement('button');
        delBtn.textContent = 'Delete';
        delBtn.className = 'danger';
        delBtn.addEventListener('click', () => deleteItem(item.id));

        const editBtn = document.createElement('button');
        editBtn.textContent = 'Edit';
        editBtn.addEventListener('click', () => enterEditMode(li, item));

        actions.appendChild(viewBtn);
        actions.appendChild(editBtn);
        actions.appendChild(delBtn);

        li.appendChild(txt);
        li.appendChild(actions);
        ul.appendChild(li);
    });
}

function enterEditMode(li, item) {
    // replace content with editable fields
    li.innerHTML = '';
    const form = document.createElement('div');
    form.className = 'edit';

    const numberInput = document.createElement('input');
    numberInput.value = item.number;
    numberInput.placeholder = '10 digits';

    const pointInput = document.createElement('input');
    pointInput.value = item.point_to || '';
    pointInput.placeholder = 'point_to';

    const saveBtn = document.createElement('button');
    saveBtn.textContent = 'Save';
    saveBtn.addEventListener('click', async () => {
        const payload = { number: numberInput.value.trim(), point_to: pointInput.value.trim() || undefined };
        try {
            showStatus('Saving...');
            const res = await fetch(`${baseUrl}/phone_numbers/${item.id}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            if (res.ok) {
                showStatus('Saved');
                await loadList();
                return;
            }
            const body = await res.json().catch(() => ({}));
            showStatus(_formatErrorBody(body, res.status), true);
        } catch (err) {
            showStatus('Could not save', true);
            console.error(err);
        }
    });

    const cancelBtn = document.createElement('button');
    cancelBtn.textContent = 'Cancel';
    cancelBtn.addEventListener('click', () => loadList());

    form.appendChild(numberInput);
    form.appendChild(pointInput);
    form.appendChild(saveBtn);
    form.appendChild(cancelBtn);
    li.appendChild(form);
}

async function viewItem(id) {
    showStatus('Loading item...');
    try {
        const res = await fetch(`${baseUrl}/phone_numbers/${id}`);
        if (res.status === 404) {
            showStatus('Item not found', true);
            await loadList();
            return;
        }
        if (!res.ok) throw new Error(`Status ${res.status}`);
        const item = await res.json();
        alert(`ID: ${item.id}\nNumber: ${fmtNumber(item.number)}\nPoint to: ${item.point_to || ''}\nLabel: ${item.label || ''}\nUsage: ${item.usage || ''}`);
        showStatus('');
    } catch (err) {
        showStatus('Could not fetch item', true);
        console.error(err);
    }
}

async function deleteItem(id) {
    if (!confirm('Delete this number?')) return;
    showStatus('Deleting...');
    try {
        const res = await fetch(`${baseUrl}/phone_numbers/${id}`, { method: 'DELETE' });
        if (res.status === 404) {
            showStatus('Item not found', true);
            await loadList();
            return;
        }
        if (res.status === 204) {
            showStatus('Deleted');
            await loadList();
            return;
        }
        throw new Error(`Unexpected status ${res.status}`);
    } catch (err) {
        showStatus('Could not delete item', true);
        console.error(err);
    }
}

async function addNumber(ev) {
    ev.preventDefault();
    const input = document.getElementById('number');
    const pointInput = document.getElementById('point_to');
    const value = input.value.trim();
    const pointVal = pointInput.value.trim();
    if (!value) return;
    showStatus('Adding...');
    try {
        const res = await fetch(`${baseUrl}/phone_numbers`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ number: value, point_to: pointVal || undefined }),
        });
        if (res.status === 201) {
            input.value = '';
            pointInput.value = '';
            showStatus('Added');
            await loadList();
            return;
        }
        const body = await res.json().catch(() => ({}));
        showStatus(_formatErrorBody(body, res.status), true);
    } catch (err) {
        showStatus('Could not add number', true);
        console.error(err);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('addForm').addEventListener('submit', addNumber);
    loadList();
});
