<template>
  <div class="port-status">
    <h1>Port Status</h1>
    <p>Test Numbers: 425.501.7838 | 206.467.5062</p>
    <div class="port-status-grid">
      <table>
        <thead>
          <tr>
            <th class="sortable" @click="sortTable('TN')">Phone Number</th>
            <th class="sortable" @click="sortTable('ring_to')">Ring To</th>
            <th class="sortable" @click="sortTable('DNIS')">DNIS</th>
            <th class="sortable" @click="sortTable('usage')">Usage</th>
            <th class="sortable" @click="sortTable('notes')">Notes</th>
            <th class="sortable" @click="sortTable('order_num')">Order #</th>
            <th class="sortable" @click="sortTable('port_date')">Port Date</th>
            <th class="sortable" @click="sortTable('pbx_dst')">PBX Destination</th>
            <th class="sortable" @click="sortTable('last_call')">Last Call</th>
            <th class="sortable" @click="sortTable('call_count')">Call Count</th>
            <th class="sortable" @click="sortTable('last_call')">Last Tested</th>
            <th class="sortable" @click="sortTable('test_count')">Test Count</th>
            <th class="sortable" @click="sortTable('rcvr_prefix')">RCVR Prefix</th>
            <th class="sortable" @click="sortTable('last_cs_no')">Last CS#</th>
            <th class="sortable" @click="sortTable('LastHour')">LastHour</th>
            <th class="sortable" @click="sortTable('last_cid')">LastCID</th>
            <th class="sortable" @click="sortTable('avg_dur')">Avg Duration</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="port in portStatus" :key="port.TN" :class="{ pending: port.is_pending, loading: isLoading, testNeeded: rcvrTestNeeded(port), elevTestNeeded: elevTestNeeded(port) }">
            <td>
              <a :href="`tel:91${port.TN}`" @click="pending(port)">{{ port.TN }}</a>
            </td>
            <td @dblclick="enableEditing(port, 'ring_to')">
              <template v-if="isEditing(port, 'ring_to')">
                <input v-model="port.editableValues.ring_to" @blur="saveEdit(port, 'ring_to')" @keyup.enter="saveEdit(port, 'ring_to')" />
              </template>
              <template v-else>
                {{ port.ring_to }}
              </template>
            </td>
            <td @dblclick="enableEditing(port, 'DNIS')" :class="{ 'badDNIS': isBadDNIS(port) }">
              <template v-if="isEditing(port, 'DNIS')">
                <input v-model="port.editableValues.DNIS" @blur="saveEdit(port, 'DNIS')" @keyup.enter="saveEdit(port, 'DNIS')" />
              </template>
              <template v-else>
                {{ port.DNIS }}
              </template>
            </td>
            <td @dblclick="enableEditing(port, 'usage')">
              <template v-if="isEditing(port, 'usage')">
                <input v-model="port.editableValues.usage" @blur="saveEdit(port, 'usage')" @keyup.enter="saveEdit(port, 'usage')" />
              </template>
              <template v-else>
                {{ port.usage }}
              </template>
            </td>
            <td class="notes" @dblclick="enableEditing(port, 'notes')">
              <template v-if="isEditing(port, 'notes')">
                <input v-model="port.editableValues.notes" @blur="saveEdit(port, 'notes')" @keyup.enter="saveEdit(port, 'notes')" />
              </template>
              <template v-else>
                {{ port.notes }}
              </template>
            </td>
            <td>{{ port.order_num }}</td>
            <td>{{ formatDate(port.port_date) }}</td>
            <td>{{ port.pbx_dst }}</td>
            <td :title="port.last_call">{{ getRelativeTime(port.last_call) }}</td>
            <td>{{ port.call_count }}</td>
            <td :title="port.last_tested">{{ getRelativeTime(port.last_tested) }}</td>
            <td>{{ port.test_count }}</td>
            <td>{{ port.rcvr_prefix }}</td>
            <td>{{ port.last_cs_no }}</td>
            <td>{{ formatHr(port.LastHour) }}</td>
            <td>{{ port.last_cid }}</td>
            <td>{{ formatDuration(port.avg_dur) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { inject } from 'vue';
import { useRoute, useRouter } from 'vue-router';

export default {
  name: 'PortStatus',
  data() {
    return {
      portStatus: [],
      sortColumn: '',
      sortAsc: true,
      isLoading: false,
      setLoading: null,
      setRefreshCallback: null,
      currentlyEditing: null,
    };
  },
  methods: {
    async fetchPortStatus() {
      if (this.setLoading) this.setLoading(true);

      try {
        const response = await fetch('http://localhost:8000/port_status');
        this.portStatus = await response.json();
        this.portStatus.forEach(port => {
          port.editableValues = { ...port };
        });
        if (this.sortColumn) {
          this.sortTable(this.sortColumn, true);
        }
      } catch (error) {
        console.error('Error fetching port status:', error);
      } finally {
        if (this.setLoading) this.setLoading(false);
      }
    },
    enableEditing(port, field) {
      this.currentlyEditing = { port, field };
    },
    isEditing(port, field) {
      return this.currentlyEditing && this.currentlyEditing.port === port && this.currentlyEditing.field === field;
    },
    async saveEdit(port, field) {
      try {
        const updatedValue = port.editableValues[field];
        const response = await fetch(`http://localhost:8000/port_status/${port.TN}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ [field]: updatedValue }),
        });

        if (!response.ok) {
          throw new Error('Failed to save data');
        }

        port[field] = updatedValue;
      } catch (error) {
        console.error('Error saving data:', error);
      } finally {
        this.currentlyEditing = null;
      }
    },
    formatPhoneNumber(phone) {
      if (!phone) return '';
      const cleaned = ('' + phone).replace(/\D/g, '');
      const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
      if (match) {
        return '(' + match[1] + ') ' + match[2] + '-' + match[3];
      }
      return phone;
    },
    pending(port) {
      port.is_pending = true;
    },
    rcvrTestNeeded(port) {
      return port.usage.toLowerCase().indexOf('rcvr') !== -1 && (!port.call_count || port.call_count < 1) && (!port.test_count || port.test_count < 1);
    },
    elevTestNeeded(port) {
      return port.usage.toLowerCase().indexOf('elev') !== -1 && (!port.call_count || port.call_count < 1) && (!port.test_count || port.test_count < 1);
    },
    isBadDNIS(port) {
      if (!port.DNIS) return false;
      const dnis = port.DNIS.trim();
      if (!port.ring_to || port.ring_to.length < 10) return false;
      console.log('Comparing', port.ring_to.slice(-4), 'to', dnis);
      return port.ring_to.slice(-4) !== dnis;
    },
    formatDate(dateString) {
      if (!dateString) return '';
      return dateString;
    },
    sortTable(column, refresh = false) {
      const route = this.$route;
      const router = this.$router;

      if (!refresh) {
        if (this.sortColumn === column) {
          this.sortAsc = !this.sortAsc;
        } else {
          this.sortColumn = column;
          this.sortAsc = true;
        }
      }

      // Update the URL with sort parameters
      router.push({
        path: route.path,
        query: {
          ...route.query,
          sortColumn: this.sortColumn,
          sortAsc: this.sortAsc
        }
      });

      this.portStatus.sort((a, b) => {
        let valA = a[column];
        let valB = b[column];
        // Handle null/undefined
        if (valA == null) valA = '';
        if (valB == null) valB = '';
        // Numeric sort if both are numbers
        if (!isNaN(valA) && !isNaN(valB)) {
          return this.sortAsc ? valA - valB : valB - valA;
        }
        // Date sort for date columns
        if (column === 'port_date' || column === 'last_call') {
          return this.sortAsc
            ? new Date(valA) - new Date(valB)
            : new Date(valB) - new Date(valA);
        }
        // String sort
        valA = valA.toString().toLowerCase();
        valB = valB.toString().toLowerCase();
        if (valA < valB) return this.sortAsc ? -1 : 1;
        if (valA > valB) return this.sortAsc ? 1 : -1;
        return 0;
      });
    },
    getRelativeTime(date) {
        const now = new Date();
        if (!date) return '';
        if (!(date instanceof Date)) {
            date = new Date(date);
        }
        const diffInSeconds = Math.round((date.getTime() - now.getTime()) / 1000);

        const cutoffs = [60, 3600, 86400, 86400 * 7, 86400 * 30, 86400 * 365, Infinity];
        const units = ["second", "minute", "hour", "day", "week", "month", "year"];

        const unitIndex = cutoffs.findIndex(cutoff => cutoff > Math.abs(diffInSeconds));
        const divisor = unitIndex ? cutoffs[unitIndex - 1] : 1;

        const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' }); // 'en' for English, adjust as needed

        return rtf.format(Math.floor(diffInSeconds / divisor), units[unitIndex]);
    },

    formatDuration(seconds) {
      if (!seconds) return '';
      const minutes = Math.floor(seconds / 60);
      const remainingSeconds = seconds % 60;
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    },
    formatHr(hr) {
      if (hr == null) return '';
      return hr.slice(4,6) + '-' + hr.slice(6,8) + ' ' + hr.slice(8,10) + ':00';
    },
    refreshData() {
      this.fetchPortStatus();
    }
  },
  created() {
    this.setLoading = inject('setLoading');
    this.setRefreshCallback = inject('setRefreshCallback');

    if (this.setRefreshCallback) {
      this.setRefreshCallback(this.refreshData);
    }
  },
  mounted() {
    const route = this.$route;

    // Check for sort parameters in the URL
    if (route.query.sortColumn) {
      this.sortColumn = route.query.sortColumn;
      this.sortAsc = route.query.sortAsc === 'true';
      this.sortTable(this.sortColumn, true);
    }

    this.fetchPortStatus();
  }
};
</script>

<style scoped>
.port-status {
  padding: 20px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  background-color: #f5f5f5;
}

tr:hover {
  background-color: #f5f5f5;
}

td {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}

td:nth-child(5) { /* Notes column */
  max-width: 300px;
  white-space: normal;
}
tr.pending {
    background: yellow;
}
td.notes {
    font-size: 10px;
}
.refresh-button {
  margin-bottom: 10px;
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.refresh-button:hover {
  background-color: #0056b3;
}
.loading-indicator {
  margin: 10px 0;
  font-size: 16px;
  color: #007bff;
}
tr.loading {
    opacity: 0.5;
}
tr.testNeeded {
    background: #ffcccc;
}
tr.elevTestNeeded {
    background: #ffebcc;
}
td.badDNIS {
    background: #fe9524;
}
</style>