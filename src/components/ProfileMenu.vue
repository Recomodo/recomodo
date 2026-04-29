<script setup lang="ts">
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


async function handleDeleteUser() {
  try {
    await raz();
    await client.models.UserProfile.delete({id: identifiant.value ?? ''});
    await deleteUser();
    router.push('/')
  } catch (error) {
    console.log(error);
  }
}

const userRatings= ref<Array<Schema['Rating']["type"]>>([]);
async function raz(){
  try{
    if (identifiant.value) {
      //await client.models.Rating.delete({userId: identifiant.value}) 
      // //ça supprime pas => je cherche les id unique puis je map

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
    onMounted(()=> {
        document.removeEventListener("click",handleClickOutside);
    })

</script>


<template>
    <div class="profileContainer" ref="menuRef">
        <!--<div class="avatar" @click="toggleMenu ">
            <font-awesome-icon icon="fa-solid fa-circle-user" size="lg" style="color: white;" />
        </div>-->
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

<style scoped>
.profileContainer {
  position: relative;
}

.avatar {
  cursor: pointer;
  width: 30px; height: 30px;
  border-radius: 50%;
  background: #521c5d;
  border: 2px solid #7a2a8a;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 600;
  color: #e9d5ff;
}

.dropdown {
  position: absolute;
  right: 0;
  top: 50px;
  width: 400px;
  height:300px;
  background: #15001d;
  border: 1px solid #7a2a8a;
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
  z-index: 100;
  box-shadow:
    0 0 0 1px rgba(108, 63, 197, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

/* Bande violette en haut */
.dropdown::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: #7a2a8a;
  border-radius: 12px 12px 0 0;
}

.name {
  font-size: 15px;
  font-weight: 600;
  color: #e9d5ff;
  margin: 0 0 4px;
}

.email {
  font-size: 13px;
  color: #b17fc5;
  margin: 0 0 1.25rem;
}

/* Séparateur */
.email::after {
  content: '';
  display: block;
  margin-top: 1rem;
  border-top: 1px solid rgba(108, 63, 197, 0.35);
}

.gestion {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.gestion button {
  display: block;
  width: 100%;
  text-align: left;
  background: none;
  border: none;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  font-size: 14px;
  color: #bd94d6;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}

.gestion button:hover {
  background: rgba(159, 58, 237, 0.25);
  color: #e9d5ff;
}

/* Bouton Delete en rouge discret */
.gestion button:last-child {
  color: #f87171;
  margin-top: 4px;
  border-top: 1px solid rgba(108, 63, 197, 0.2);
  padding-top: 0.6rem;
}

.gestion button:last-child:hover {
  background: rgba(248, 113, 113, 0.12);
  color: #fca5a5;
}
.avatar2{
  width: 48px; height: 48px;
  border-radius: 50%;
  background: #521c5d;
  border: 2px solid #7a2a8a;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; font-weight: 600;
  color: #e9d5ff;
  margin-bottom: 1rem;
}
</style>