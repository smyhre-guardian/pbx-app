<template>
  <div class="phone-number-dropdown">
    <span @click="toggleDropdown" class="phone-number">{{ phoneNumber }}</span>
    <div v-if="dropdownVisible" class="dropdown-menu">
      <a v-if="showDial" :href="`tel:91${phoneNumber}`" @click="doDial">Dial Number</a>
      <a v-if="showCdr" :href="`/call-records?q=${phoneNumber}`" target="_blank" @click="closeDropdown">View CDRs</a>
      <a v-if="showLookup" :href="`/phone-lookup?phone=${phoneNumber}`" target="_blank" @click="closeDropdown">Lookup CID</a>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PhoneNumberDropdown',
  props: {
    phoneNumber: {
      type: String,
      required: true
    },
    showCdr: {
      type: Boolean,
      default: true
    },
    showDial: {
      type: Boolean,
      default: true
    },
    showLookup: {
      type: Boolean,
      default: true
    },
    onDial: {
      type: Function,
      default: null
    }
  },
  data() {
    return {
      dropdownVisible: false
    };
  },
  methods: {
    toggleDropdown() {
      this.dropdownVisible = !this.dropdownVisible;
    },
    closeDropdown() {
      this.dropdownVisible = false;
    },
    doDial(event) {
      if (this.onDial) {
        this.onDial(this.phoneNumber);
      }
      this.closeDropdown();
    }
  }
};
</script>

<style scoped>
.phone-number-dropdown {
  /* position: relative; */
  display: inline-block;
  cursor: pointer;
}

.phone-number {
  color: blue;
  text-decoration: underline;
}

.dropdown-menu {
  position: absolute;
  /* top: 100%; */
  /* left: 0; */
  background: white;
  border: 1px solid #ccc;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  padding: 10px;
  display: flex;
  flex-direction: column;
}

.dropdown-menu a {
  color: black;
  text-decoration: none;
  margin: 5px 0;
}

.dropdown-menu a:hover {
  text-decoration: underline;
}
</style>