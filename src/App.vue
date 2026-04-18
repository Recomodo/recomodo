<script setup lang="ts">
import { Authenticator } from '@aws-amplify/ui-vue';
import "@aws-amplify/ui-vue/styles.css";
import Nav from './components/Nav.vue'
</script>

<template>
  <main>
    <authenticator>
      <template v-slot="{user, signOut}">
        <router-view/>
        <!--<Nav/>-->
        <!--<button  @click="signOut">Sign Out </button>-->
      </template>
    </authenticator>
  </main>
</template>
