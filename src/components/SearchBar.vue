<template>
  <input type="search" placeholder="Search...  🔍" id="titre_film" class="searchBar" v-model="titre" @keydown.enter="emitSearch" > <!--v-model => titre.value="ce que l'utilisateur entre" -->
</template>

<script setup lang="ts">
import "@/assets/search.css";
import {ref,watch} from "vue";

const titre=ref("");
const emit = defineEmits<{
    (e:"search", value:string): void;
}>();

function emitSearch(){
    clearTimeout(timeout);
    emit("search", titre.value)
}
let timeout: ReturnType<typeof setTimeout>;
watch(titre, (val) => {
  clearTimeout(timeout);
  if (!val.trim()) {
    emit("search", ""); // remet la homepage immédiatement
    return;
  }
  timeout = setTimeout(() => {
    emit("search", val);
  }, 400);
});


</script>
