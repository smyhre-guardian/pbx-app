<template>
  <main>
    <h1 @dblclick="showButton = !showButton">About</h1>
    <p v-if="showButton">
      <button @click="pull()">Pull code from git</button>
    </p>
    <p>
      The PBX layout:
    </p>
    <img src="@/assets/PBX.drawio.png" alt="PBX Layout" style="max-width:100%;height:auto;" />
    <p>
      <hr/>
      <p>
        There are <strong>2 SBC HA redundant devices</strong> that act as SIP firewalls and intelligent routers for SIP traffic. They are connected to both Comcast and Lumen ISPs, and both SEA and CHI Sinch servers. Sinch is programmed to hit both Lumen and Comcast in a round-robin fashion, but there is still a ticket open confirming that is the case (doesn't seem to be).
      </p>
      <p>
        There are <strong>2 PBX servers</strong> that handle routing for incoming calls terminating at the SBC. The SBC utilizes both of these PBX servers in a round-robin fashion.
      </p>
      <p>
        The PBX translates incoming DNIS (called number) to any other DNIS that the Avaya might expect. This mapping was prepared by Vern and later refined by Steven based on existing translations.
      </p>
      <p>
        The call is then passed in a round-robin fashion to the Adtran 644 over SIP, with a prefix to direct the call. Currently, the only prefix used is <strong>11</strong>, since everything is going to the Avaya:
      </p>
      <ul>
        <li><strong>11</strong> prefix &rarr; To Avaya</li>
        <li><strong>12</strong> prefix &rarr; From Avaya</li>
        <li><strong>13</strong> prefix &rarr; To 550</li>
      </ul>
      <p>
        The Adtran 644 then passes the calls over two PRIs (stripping the 2-digit prefix first) and the call arrives as expected on the Avaya.
      </p>
      <p>
        The Avaya then routes normally to phones, receivers, and call trees.
      </p>
      <p>
        The only now configurable part of it is the PBX, where translations are made. A web tool was built to manage this in a predictable way without using the command line and breaking anything.
      </p>
      <p>
        Should you wish to break things, the SSH credentials are in the password store.
      </p>
    </p>
  </main>
</template>

<script setup>
import { ref } from 'vue'
const showButton = ref(false);
const pull = async () => {
  try {
    const res = await fetch((import.meta.env.VITE_API_URL || 'http://localhost:8000') + '/git-pull');
    const data = await res.json();
    alert('Git Pull Result:\n' + JSON.stringify(data, null, 2));
  } catch (e) {
    alert('Error during git pull: ' + e.message);
  }
}
</script>

<style>
main { max-width: 1200px; margin: 0 auto; background: white; padding: 18px; border-radius: 8px; }
</style>
