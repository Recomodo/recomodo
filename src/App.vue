<script setup lang="ts">
import { ref, onMounted } from "vue";
import { get } from "aws-amplify/api";
import { Authenticator } from '@aws-amplify/ui-vue';
import "@aws-amplify/ui-vue/styles.css";
import Todos from './components/Todos.vue'
import { AuthenticateCognitoAction } from 'aws-cdk-lib/aws-elasticloadbalancingv2-actions';

// Définition du type de la réponse de l'API REST
type DateResponse = {
  date: string;
};

// Référence pour stocker la date actuelle
const currentDate = ref("Chargement");
const errorMessage = ref("");

// Fonction pour charger la date à partir de l'API REST
async function loadDate(){
  try {
    const restOperation = get({
      apiName: "Test_API",
      path: "/date",
    });

    const {body} = await restOperation.response;
    const data = (await body.json()) as { date: string };
    currentDate.value = data.date;
  } catch (error) {
    console.error("API Error:", error);
    errorMessage.value = "Failed to load date.";
  }
}

// Charger la date lorsque le composant est monté
onMounted(() => {
  loadDate();
});

</script>

<template>
  <main>
    <authenticator>
      <template v-slot="{user, signOut}">
        <h1>Hello {{ user?.signInDetails?.loginId }}'s todo </h1>
        <p>Date du jour (API):{{ currentDate }}</p>
        <p v-if="errorMessage">{{ errorMessage }}</p>
        <Todos />
        <button  @click="signOut">Sign Out </button>
      </template>
    </authenticator>
  </main>
</template>

