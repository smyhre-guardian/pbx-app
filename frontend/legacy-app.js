/* Legacy plain JS frontend preserved for reference. Migrated into Vue views. */

const baseUrl = (window.__API_BASE__ && window.__API_BASE__) || "http://127.0.0.1:8000";

function fmtNumber(digits) {
    if (!digits || digits.length !== 10) return digits;
    return `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`;
}

function showStatus(msg, isError = false) {
    const el = document.getElementById('status');
    if (!el) return;
    el.textContent = msg;
    el.className = isError ? 'error' : 'ok';
    if (!msg) el.className = '';
}

function _formatErrorBody(body, status) {
    if (!body) return `Error: ${status}`;
    if (body.detail) {
        const d = body.detail;
        if (Array.isArray(d)) {
            return d.map(e => {
                if (e && e.msg) {
                    const loc = Array.isArray(e.loc) ? e.loc.join('.') : e.loc;
                    return loc ? `${loc}: ${e.msg}` : e.msg;
                }
                return typeof e === 'string' ? e : JSON.stringify(e);
            }).join('; ');
        }
        if (typeof d === 'string') return d;
        return JSON.stringify(d);
    }
    if (typeof body === 'string') return body;
    try { return JSON.stringify(body); } catch (e) { return `Error: ${status}`; }
}

// ... rest of original app.js logic omitted for brevity; original file is preserved in repo history.
