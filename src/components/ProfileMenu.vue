<script setup lang="ts">
import "@/assets/profileMenu.css";
import { signOut } from 'aws-amplify/auth';
import { deleteUser } from 'aws-amplify/auth';
import type {Schema} from "../../amplify/data/resource";
import { generateClient } from 'aws-amplify/data';
import{onMounted, ref, onBeforeUnmount} from "vue";
import { getCurrentUser } from 'aws-amplify/auth';
import { useRouter } from 'vue-router';

const router = useRouter();

const email = ref<string | null>(null);
const identifiant = ref<string | null>(null);
  const userName= ref<string | null>(null);
onMounted(async () => {
  const user = await getCurrentUser();
  email.value = user.signInDetails?.loginId ?? null;
  identifiant.value = user.userId;
  const profile  = await client.models.UserProfile.get({id: identifiant.value ?? ''});
  userName.value = profile.data?.username ?? null;
});

const client = generateClient<Schema>();

async function signout(){
  try{
    await signOut()
    router.push('/')
  }catch(error){
    console.log(error);
  }
}
const userRatings= ref<Array<Schema['Rating']["type"]>>([]);

async function handleDeleteUser() {
  try {
    if (identifiant.value) {
      const {data} = await client.models.Rating.list({filter:{userId:{eq:identifiant.value}}})
      userRatings.value = data ?? [];
      await Promise.all(userRatings.value.map(rating => client.models.Rating.delete({id: rating.id})));
    
     await client.models.UserProfile.delete({id: identifiant.value ?? ''});
     await deleteUser();
     router.push('/')
    }
  } catch (error) {
    console.log(error);
  }
}


async function raz(){
  try{
    if (identifiant.value) {
      const {data} = await client.models.Rating.list({filter:{userId:{eq:identifiant.value}}})
      userRatings.value = data ?? [];
      await Promise.all(userRatings.value.map(rating => client.models.Rating.delete({id: rating.id})));
      await client.models.UserProfile.update({
        id:identifiant.value,
        hasCompleted:false
      })
      location.href = '/'
    }

  }catch(error){
    console.log(error);
  }
}


const isOpen = ref(false);
function toggleMenu(){
    isOpen.value=!isOpen.value;
}
const menuRef= ref<HTMLElement | null>(null);
    function handleClickOutside(e:MouseEvent){
        if(menuRef.value && !menuRef.value.contains(e.target as Node)){
            isOpen.value=false;
        }

    }
    onMounted(()=> {
        document.addEventListener("click",handleClickOutside);
    })
    onBeforeUnmount(()=> {
        document.removeEventListener("click",handleClickOutside);
    })

</script>


<template>
    <div class="profileContainer" ref="menuRef">
        <div class="avatar" @click="toggleMenu">
          {{ userName?.charAt(0).toUpperCase() }}
        </div>
        
        <div v-if="isOpen" class="dropdown">
           <div class="avatar2">
                {{ userName?.charAt(0).toUpperCase() }}
            </div>
            <p class="name">User name : {{ userName }}</p>
            <p class="email">Email : {{ email }}</p>
            <div class="gestion">
            <button  @click="signout()">Sign Out</button>
            <button @click="raz()">Reset</button>
            <button @click="handleDeleteUser()">Delete account</button>
            </div>
        </div>
    </div>
</template>

