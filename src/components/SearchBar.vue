<template>

<input type="text" placeholder="Recherche " id="titre_film" class="searchBar" v-model="titre" @keyup.enter="emitSearch"> <!--v-model => titre.value="ce que l'utilisateur entre" -->

</template>

<script setup lang="ts">

import {ref} from "vue";

const titre=ref("");
const emit = defineEmits<{
    (e:"search", value:string): void;
}>();

function emitSearch(){
    emit("search", titre.value)
}
//cas si je fait on input
/*let timeout:any;
function onInput(){
    clearTimeout(timeout);
    timeout=setTimeout(()=>{
        emit("search",titre.value);
    },300);
}*/
</script>