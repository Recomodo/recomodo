<script setup lang="ts">
import { Authenticator } from '@aws-amplify/ui-vue';
import "@aws-amplify/ui-vue/styles.css";
import Todos from './components/Todos.vue'
import Nav from './components/Nav.vue'
import { AuthenticateCognitoAction } from 'aws-cdk-lib/aws-elasticloadbalancingv2-actions';
</script>

<template>
  <main>
    <authenticator>
      <template v-slot="{user, signOut}">
        <!--<h1>Hello {{ user?.signInDetails?.liginId }}'s todo</h1>-->
        <!--<Todos />-->
        <router-view/>
        <!--<Nav/>-->
        <!--<button  @click="signOut">Sign Out </button>-->
      </template>
    </authenticator>
  </main>
</template>

