<script setup lang="ts">
import { signOut } from 'aws-amplify/auth';
import { deleteUser } from 'aws-amplify/auth';
import { getCurrentUser } from 'aws-amplify/auth';
import selectedGenres from './FirstSigninPage.vue';
import type {Schema} from "../../amplify/data/resource";
import { generateClient } from 'aws-amplify/data';
import{onMounted, ref} from "vue";


const client = generateClient<Schema>();

const { data, errors } = await client.models.Genre.list();
console.log("Genres:", data);
console.log("Errors:", errors);


async function signout(){
  try{
await signOut()
  }catch(error){
    console.log(error);
  }
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
      <!-- <FirstSigninPage/> -->
      <div v-for="genre in selectedGenres" :key="genre.genreId">
        <p>{{ genre.name }}</p>
      </div>
    </div>

    <div class="userFonctions">
      <h5>{{}}</h5>
     <button  @click="signout()">Sign Out</button>
     <button @click="handleDeleteUser()">Delete account</button>
  </div>
</div>
</template>

<style scoped>
.userFonctions{
border: 1px solid #ccc;
border-radius: 12px;
padding: 10px;
width:35%; 
height:max-content;
display:flex;
flex-direction:column;
}


</style>