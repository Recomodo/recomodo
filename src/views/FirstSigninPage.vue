<script setup lang="ts">
//récuperer le liste des genres dans un tableau
import { ref, onMounted } from 'vue';

//api
import type {Schema} from "../../amplify/data/resource";
import { generateClient } from 'aws-amplify/data';
const client = generateClient<Schema>();
const genresSections = ref<Array<Schema['Genre']["type"]>>([]);

console.log("MODELS:", client.models);
const res = await client.models.Genre.list();

console.log("RAW RESPONSE:", res);
console.log("DATA:", res.data);
console.log("ERRORS:", res.errors);
onMounted(async()=>{
   const{data}=await client.models.Genre.list({
      limit: 20,
   });
   console.log("GENRES:", data);
   genresSections.value=data;
})

const maxSelection = 3;
const selectedGenres = ref<number[]>([]);

function clickedGenre(genreId: number) {
   if (selectedGenres.value.includes(genreId)) {
      selectedGenres.value = selectedGenres.value.filter(id => id !== genreId);
   } else if (selectedGenres.value.length < maxSelection) {
      selectedGenres.value.push(genreId);
   }
}

function isSelected(genreId: number) {
   return selectedGenres.value.includes(genreId);
}

function isDisabled(genreId: number) {
   return !selectedGenres.value.includes(genreId) && selectedGenres.value.length >= maxSelection;
}



</script>


<template>
   <h1>Première connexion</h1>
   <div>
      <p>veuillez sélectionner jusqu'à trois genres de films qui vous passionnent le plus. N'hésitez pas à explorer différentes catégories pour découvrir de nouveaux films et élargir vos horizons cinématographiques. Votre sélection nous permettra de vous offrir une expérience personnalisée et de vous recommander des films qui correspondent parfaitement à vos préférences.</p>
         <button class="genreSection" :class="{ selected: isSelected(genre.genreId), disabled: isDisabled(genre.genreId) }" v-for="genre in genresSections" :key="genre.id"  @click="clickedGenre(genre.genreId) ">
            <label :for="String(genre.genreId)">{{ genre.name }} </label>
         </button>
   </div>


</template>

<style scoped>
.disabled {
   pointer-events: none;
   opacity: 0.5;
}
.selected{
   background-color: rgba(107, 44, 134, 0.5);
}



</style>