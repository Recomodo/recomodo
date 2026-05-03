<template>
  <input type="search" placeholder="Search...  🔍" id="titre_film" class="searchBar" v-model="titre" @keydown.enter="emitSearch" > <!--v-model => titre.value="ce que l'utilisateur entre" -->
</template>

<script setup lang="ts">
import "@/assets/search.css";
import {ref} from "vue";

const titre=ref("");
const emit = defineEmits<{
    (e:"search", value:string): void;
}>();

function emitSearch(){
    clearTimeout(timeout);
    emit("search", titre.value)
}
let timeout: ReturnType<typeof setTimeout>;

function onInput() {
    clearTimeout(timeout);
    timeout = setTimeout(() => {
        emit("search", titre.value);
    }, 400);
}

</script>
