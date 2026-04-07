<script setup lang="ts">
import { signOut } from 'aws-amplify/auth';
import { deleteUser } from 'aws-amplify/auth';
import selectedGenres from './FirstSigninPage.vue';

async function signout(){
await signOut()
}


async function handleDeleteUser() {
  try {
    await deleteUser();
  } catch (error) {
    console.log(error);
  }
}
</script>

<template>
  <div style="display: flex; flex-direction:row; justify-content:space-around; gap: 20px;padding-block: 2rem;">
    <div style="border: 1px solid #ccc; padding: 10px;border-radius: 12px; width:55%; display:flex; flex-direction: column; align-items: center;">
      <h1>Profile Page</h1>
      <div v-for="genre in selectedGenres" :key="genre.genreId">
        <p>{{ genre.name }}</p>
      </div>
      <FirstSigninPage/>
    </div>

    <div style="border: 1px solid #ccc;border-radius: 12px; padding: 10px; width:35%; display:flex; flex-direction:column;">
     <button  @click="signout()">Sign Out</button>
     <button @click="handleDeleteUser()">Delete account</button>
  </div>
</div>
</template>

<style scoped>

</style>