<template>
  <div class="port-status">
    <h1>Port Status</h1>
    <p>Test Numbers: 425.501.7838 | 206.467.5062</p>

    <!-- Radio Buttons for Filters -->
    <div class="filters">
        <div>
            <label>
                <input type="radio" value="include" v-model="elevatorFilter" /> Include Elevators
            </label>
            <label>
                <input type="radio" value="only" v-model="elevatorFilter" /> Only Elevators
            </label>
            <label>
                <input type="radio" value="exclude" v-model="elevatorFilter" /> Exclude Elevators
            </label>
      </div>

      <div>
        <label>
            <input type="radio" value="include" v-model="receiverFilter" /> Include Receivers
        </label>
        <label>
            <input type="radio" value="only" v-model="receiverFilter" /> Only Receivers
        </label>
        <label>
            <input type="radio" value="exclude" v-model="receiverFilter" /> Exclude Receivers
        </label>
      </div>
    </div>

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
            <th class="sortable" @click="sortTable('last_tested')">Last Tested</th>
            <th class="sortable" @click="sortTable('test_count')">Test Count</th>
            <th class="sortable" @click="sortTable('rcvr_prefix')">RCVR Prefix</th>
            <th class="sortable" @click="sortTable('last_cs_no')">Last CS#</th>
            <th class="sortable" @click="sortTable('LastHour')">LastHour</th>
            <th class="sortable" @click="sortTable('last_cid')">LastCID</th>
            <th class="sortable" @click="sortTable('avg_dur')">Avg Duration</th>
            <th class="sortable" @click="sortTable('elevator_acct')">Elevator Acct</th>
            <th class="sortable" @click="sortTable('acct_status')">Acct Status</th>
            <th class="sortable" @click="sortTable('lumen_name')">Lumen Desc</th>
            <th class="sortable" @click="sortTable('lumen_point_to')">Lumen Point To</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="port in filteredPortStatus" :key="port.TN" :class="{ pending: port.is_pending, loading: isLoading, testNeeded: rcvrTestNeeded(port), elevTestNeeded: elevTestNeeded(port) }">
            <td :title="port.TN">
              <a :href="`tel:91${port.TN}`" @click="pending(port)">{{ port.TN }}</a>
            </td>
            <td :title="port.ring_to" @dblclick="enableEditing(port, 'ring_to')">
              <template v-if="isEditing(port, 'ring_to')">
                <input v-model="port.editableValues.ring_to" @blur="saveEdit(port, 'ring_to')" />
              </template>
              <template v-else>
                {{ port.ring_to }}
              </template>
            </td>
            <td :title="port.DNIS" @dblclick="enableEditing(port, 'DNIS')" :class="{ 'badDNIS': isBadDNIS(port) }">
              <template v-if="isEditing(port, 'DNIS')">
                <input v-model="port.editableValues.DNIS" @blur="saveEdit(port, 'DNIS')" />
              </template>
              <template v-else>
                {{ port.DNIS }}
              </template>
            </td>
            <td :title="port.usage" @dblclick="enableEditing(port, 'usage')">
              <template v-if="isEditing(port, 'usage')">
                <input v-model="port.editableValues.usage" @blur="saveEdit(port, 'usage')" />
              </template>
              <template v-else>
                {{ port.usage }}
              </template>
            </td>
            <td class="notes" :title="port.notes" @dblclick="enableEditing(port, 'notes')">
              <template v-if="isEditing(port, 'notes')">
                <input v-model="port.editableValues.notes" @blur="saveEdit(port, 'notes')" />
              </template>
              <template v-else>
                {{ port.notes }}
              </template>
            </td>
            <td :title="port.order_num">{{ port.order_num }}</td>
            <td :title="'last updated: ' + formatDate(port.last_updated)">{{ formatDate(port.port_date) }}</td>
            <td :title="port.pbx_dst">{{ port.pbx_dst }}</td>
            <td :title="port.last_call">{{ getRelativeTime(port.last_call) }}</td>
            <td :title="port.call_count">{{ port.call_count }}</td>
            <td :title="port.last_tested">{{ getRelativeTime(port.last_tested) }}</td>
            <td>{{ port.test_count }}</td>
            <td>{{ port.rcvr_prefix }}</td>
            <td :title="port.last_cs_no">{{ port.last_cs_no }}</td>
            <td :title="port.LastHour">{{ port.LastHour }}</td>
             <td><a v-if="port.last_cid" :href="'/phone-lookup?phone=' + port.last_cid" target="_blank">{{ port.last_cid }}</a><span v-else>{{ port.last_cid }}</span></td>
            <td :title="formatDuration(port.avg_dur)">{{ formatDuration(port.avg_dur) }}</td>
            <td :title="port.elevator_acct" :class="{'inactive': ! port.acct_status || port.acct_status[0] !== 'A'}">{{ port.elevator_acct }}</td>
            <td :title="port.acct_status">{{ port.acct_status }}</td>
            <td :title="port.lumen_name">{{ port.lumen_name }}</td>
            <td :class="{'different': !sameLast4(port.lumen_point_to, port.TN.toString(), isElev(port)) && !sameLast4(port.lumen_point_to, port.ring_to, isElev(port))}">{{ port.lumen_point_to }}</td>
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
      elevatorFilter: 'include',
      receiverFilter: 'include',
    };
  },
  computed: {
    filteredPortStatus() {
      return this.portStatus.filter(port => {
        if (this.elevatorFilter === 'exclude' && this.isElev(port)
            || this.elevatorFilter === 'only' && !this.isElev(port)) {
            return false;
        }
        if (this.receiverFilter === 'exclude' && this.isRcvr(port)
            || this.receiverFilter === 'only' && !this.isRcvr(port)
        ) {
            return false;
        }
        return true;
      });
    }
  },
  methods: {
    async fetchPortStatus() {
      if (this.setLoading) this.setLoading(true);

      try {
        const baseUrl = import.meta.env.VITE_API_URL;
        const response = await fetch(`${baseUrl}/port_status`);
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
        const baseUrl = import.meta.env.VITE_API_URL;
        const response = await fetch(`${baseUrl}/port_status/${port.TN}`, {
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
        port.editableValues[field] = port[field]; // Revert to original value on error
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
    isElev(port) {
      return port.usage.toLowerCase().indexOf('elev') !== -1 || port.notes.toLowerCase().indexOf('elev') !== -1;
    },
    isRcvr(port) {
      return port.usage.toLowerCase().indexOf('rcvr') !== -1;
    },
    elevTestNeeded(port) {
      return port.usage.toLowerCase().indexOf('elev') !== -1 && (!port.call_count || port.call_count < 1) && (!port.test_count || port.test_count < 1);
    },
    isBadDNIS(port) {
      if (!port.DNIS) return false;
      const dnis = port.DNIS.trim();
      if (!port.ring_to || port.ring_to.length < 10) return false;
      return port.ring_to.slice(-4) !== dnis;
    },
    sameLast4(a, b, isElev = false) {
      if (!a || !b || a.length < 4 || b.length < 4) return false;
      var len = isElev ? -3 : -4;
      return a.trim().slice(len) === b.trim().slice(len);
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
        if (column === 'port_date' || column === 'last_call' || column === 'last_tested') {
            if (!valA || !valB) return valA ? -1 : 1;
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
  position: sticky;
  top: 50px;
  z-index: 1;
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

tr.pending {
    background: yellow;
}
td.notes {
    font-size: 10px;
    max-width: 300px;
    white-space: normal;
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
td.inactive {
    color: red;
}
td.different {
    color: #fe9524
}
.filters {
  margin-bottom: 20px;
}
.filters label {
  margin-right: 15px;
}
</style>