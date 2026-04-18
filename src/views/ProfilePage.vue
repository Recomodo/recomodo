<script setup lang="ts">
import { signOut } from 'aws-amplify/auth';
import { deleteUser } from 'aws-amplify/auth';
import type {Schema} from "../../amplify/data/resource";
import { generateClient } from 'aws-amplify/data';
import{onMounted, ref} from "vue";
import { getCurrentUser } from 'aws-amplify/auth';
import { useRouter } from 'vue-router';

const router = useRouter();

const email = ref<string | null>(null);
const identifiant = ref<string | null>(null);
onMounted(async () => {
  const user = await getCurrentUser();
  email.value = user.signInDetails?.loginId ?? null;
  identifiant.value = user.userId;
});

const client = generateClient<Schema>();

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

async function raz(){
  try{
    if (identifiant.value) {
      await client.models.Rating.delete({id: identifiant.value})
      await client.models.UserProfile.update({
        id:identifiant.value,
        hasCompleted:false
      })
      router.push('/firstsignin')
    }
  }catch(error){
    console.log(error);
  }
}
</script>

<template>
  <div style="display: flex; flex-direction:row; justify-content:space-around; gap: 20px;padding-block: 2rem;">
    <div style="border: 1px solid #ccc; padding: 10px;border-radius: 12px; width:55%; display:flex; flex-direction: column; align-items: center;">
      <h1>Profile Page</h1>
    </div>
   <div class="raz">
    <div class="userFonctions">
      <p>{{ email }}</p>
      <p>{{ identifiant }}</p>

     <button  @click="signout()">Sign Out</button>
     <button @click="raz()">raz</button>
     <button @click="handleDeleteUser()">Delete account</button>
    </div>
    
    </div>
 </div>
</template>

<style scoped>
.userFonctions{
border: 1px solid #ccc;
border-radius: 12px;
padding: 10px;
height:max-content;
display:flex;
flex-direction:column;
}
.raz{
  display: flex;
  width:35%; 
  flex-direction: column;
  gap: 4rem;
}

</style>
