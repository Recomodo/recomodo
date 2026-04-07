<template>

<input type="text" placeholder="Recherche" id="titre_film" class="barre_rech" v-model="titre"> <!--v-model => titre.value="ce que l'utilisateur entre" -->
<button class="boutton_rech" @click="getTitle"><font-awesome-icon icon="fa-solid fa-magnifying-glass" size="xs" style="color: white;" /></button>
</template>

<script setup lang="ts">
import {ref} from "vue";
const titre = ref("");  
    function getTitle(){
        titre.value=titre.value.toLowerCase();
       alert(titre.value);
        return titre.value
    }
 
</script>