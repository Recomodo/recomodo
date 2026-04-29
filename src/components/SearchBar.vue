<template>

<input type="search" placeholder="Search...  🔍" id="titre_film" class="searchBar" v-model="titre"  @keydown.enter="emitSearch" > <!--v-model => titre.value="ce que l'utilisateur entre" --> <!--@input="onInput"-->

</template>

<script setup lang="ts">

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
<style>
.searchBar{
    border-radius: 7px;
    padding-inline: 12px;
    padding-block: 3px;
}
.searchBar:hover{
    border-color: rgb(239, 162, 239);
}

</style>