<script setup lang="ts">
import { Authenticator } from '@aws-amplify/ui-vue';
import "@aws-amplify/ui-vue/styles.css";
import { AuthenticateCognitoAction } from 'aws-cdk-lib/aws-elasticloadbalancingv2-actions';
import Nav from '@/components/Nav.vue';
import Footer from '@/components/Footer.vue';
import FirstSigninPage from './views/FirstSigninPage.vue';

</script>

<template>
 <Nav/>
  <main>
    <authenticator>
      <template v-slot="{user, signOut}">
        <RouterView/>
        <!--<RouterView v-if="hasCompleted"/>
        <FirstSigninPage v-else-if="!hasCompleted"/>-->
      </template>
    </authenticator>
  </main>
  <Footer/>
</template>

