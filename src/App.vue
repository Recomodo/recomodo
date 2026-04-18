<script setup lang="ts">
import { Authenticator } from '@aws-amplify/ui-vue';
import "@aws-amplify/ui-vue/styles.css";
import Nav from '@/components/Nav.vue';
import Footer from '@/components/Footer.vue';
import FirstSigninPage from '@/views/FirstSigninPage.vue';

import type {Schema} from "../amplify/data/resource";
import { generateClient } from 'aws-amplify/data';
import { onMounted, ref, computed } from 'vue';
import { getCurrentUser } from 'aws-amplify/auth';

const client = generateClient<Schema>();
const profile=ref<any>();
const identifiant = ref<string>("");
onMounted(async () => {
  const user = await getCurrentUser();
  identifiant.value = user.userId;

  const {data} = await client.models.UserProfile.get({id:user.userId});
  profile.value=data;

});



</script>

<template>
 <Nav/>
  <main>
    <authenticator>
      <template v-slot="{user, signOut}">
       <!--<RouterView v-if="user.hasCompleted"/>
        <FirstSigninPage v-else-if="!user.hasCompleted"/>
        <p v-else>Loading...</p>-->

        <RouterView/>
      

      </template>
    </authenticator>
  </main>
  <Footer/>
</template>
