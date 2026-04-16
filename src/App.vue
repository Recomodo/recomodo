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
const name = ref<string>('');
const userId = ref<string>('');
const hasCompleted = ref<boolean>(false);

const GetUserProfileQuery = `
  query GetUserProfile ($id: ID!) {
    getUserProfile (id: $id) {
      userId
      username
      hasCompleted
    }
  }
`;

onMounted(async () => {
  try {
    const user = await getCurrentUser();
    userId.value = user.userId;
    console.log("Current User ID:", userId.value);
    const res = await client.graphql({
      query: GetUserProfileQuery,
      variables: { id: userId.value }
    });
    
    const profile = res.data?.getUserProfile;
    hasCompleted.value = profile?.hasCompleted ?? false;
    name.value = profile?.username ?? '';

    console.log("User Profile:", profile);
  } catch (error) {
    console.error("Error fetching user profile:", error);
  }
});


</script>

<template>
 <Nav/>
  <main>
    <authenticator>
      <template v-slot="{user, signOut}">
        <RouterView/>
        <!--<RouterView v-if="hasCompleted"/>-->
       <!--<FirstSigninPage v-else-if="!hasCompleted"/>-->
        <p>user: {{ name }}</p>
        <p>hasCompleted: {{ hasCompleted }}</p>
      </template>
    </authenticator>
  </main>
  <Footer/>
</template>

