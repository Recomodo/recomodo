<script setup lang="ts">
import { Authenticator, useAuthenticator } from '@aws-amplify/ui-vue'
import "@aws-amplify/ui-vue/styles.css"
import Nav from '@/components/Nav.vue'
import Footer from '@/components/Footer.vue'
import type { Schema } from "../amplify/data/resource"
import { generateClient } from 'aws-amplify/data'
import { watch, ref } from 'vue'

const client = generateClient<Schema>()
const profile = ref<any>(null)
const auth = useAuthenticator()

watch(() => auth.user, async (newUser) => {
  if (newUser) {
    try {
      const { data } = await client.models.UserProfile.get({ id: newUser.userId })
      if (!data) {
        const { data: newProfile } = await client.models.UserProfile.create({
          id: newUser.userId,
          username: '',
          hasCompleted: false,
        })
        profile.value = newProfile
      } else {
        profile.value = data
      }
    } catch (error) {
      console.error('Erreur UserProfile:', error)
    }
  }
}, { immediate: true })
</script>

<template>
  <Nav/>
  <main>
    <Authenticator>
      <template v-slot="{ user, signOut }">
        <p v-if="profile === null">Chargement...</p>
        <RouterView v-else/>
      </template>
    </Authenticator>
  </main>
  <Footer/>
</template>