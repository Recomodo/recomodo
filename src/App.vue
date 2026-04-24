<script setup lang="ts">
import { Authenticator, useAuthenticator } from '@aws-amplify/ui-vue'
import "@aws-amplify/ui-vue/styles.css"
import Nav from '@/components/Nav.vue'
import Footer from '@/components/Footer.vue'
import { generateClient } from 'aws-amplify/data'
import type { Schema } from "../amplify/data/resource"
import { watch, ref } from 'vue'
import FirstSigninPage from '@/views/FirstSigninPage.vue'

const client = generateClient<Schema>()
const profile = ref<any>(null)
const auth = useAuthenticator()

watch(() => auth.user, async (newUser) => {
  if (newUser) {
    try {
      // On cherche le profil avec l'userId de Cognito
      const { data } = await client.models.UserProfile.get({ id: newUser.userId })
      
      if (!data) {
        // Première connexion → on crée le profil
        // Première connexion → on génère le username depuis l'email
        const email = newUser.signInDetails?.loginId ?? ''
        const username = email.split('@')[0]  // ← "Adriana.Nganzu" depuis "Adriana.Nganzu@gmail.com"
        const { data: newProfile } = await client.models.UserProfile.create({
          id: newUser.userId,
          username: username,
          hasCompleted: false,
        })
        profile.value = newProfile
      } else {
        // Profil existe → on le stocke
        profile.value = data
      }
    } catch (error) {
      console.error('Erreur UserProfile:', error)
    }
  }
}, { immediate: true }) // immediate:true pour déclencher dès le démarrage si déjà connecté
</script>

<template>
 
  <main>
    <Authenticator>
      <template v-slot="{ user, signOut }">
         <Nav/>
        <!-- Chargement -->
        <p v-if="profile === null">Chargement...</p>

        <!-- Questionnaire si première connexion -->
        <FirstSigninPage v-else-if="!profile.hasCompleted"/>

        <!-- App normale -->
        <RouterView v-else/>
        <!--<RouterView/>-->
      <Footer/>
      </template>
    </Authenticator>
  </main>
</template>