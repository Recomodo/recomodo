<script setup lang="ts">
//récuperer le liste des genres dans un tableau
import { ref } from 'vue';
const genresSections=[      // à remplacer par l'API
    {
        genreId: "1",
        name: "Action",
    },
    {
        genreId: "2",
        name: "Comedy"
    },
    {
        genreId: "3",
        name: "Drama"
    },
    {
        genreId: "4",
        name: "Horror"
    },
    {
        genreId: "5",
        name: "Science Fiction"
    },
    {
        genreId: "6",
        name: "Romance"
    }
];

const maxSelection = 3;
const selectedGenres = ref<string[]>([]);

function clickedGenre(genreId: string) {
   if (selectedGenres.value.includes(genreId)) {
      selectedGenres.value = selectedGenres.value.filter(id => id !== genreId);
   } else if (selectedGenres.value.length < maxSelection) {
      selectedGenres.value.push(genreId);
   }
}

function isSelected(genreId: string) {
   return selectedGenres.value.includes(genreId);
}

function isDisabled(genreId: string) {
   return !selectedGenres.value.includes(genreId) && selectedGenres.value.length >= maxSelection;
}



</script>


<template>
   <h1>Première connexion</h1>
   <div>
      <p>veuillez sélectionner jusqu'à trois genres de films qui vous passionnent le plus. N'hésitez pas à explorer différentes catégories pour découvrir de nouveaux films et élargir vos horizons cinématographiques. Votre sélection nous permettra de vous offrir une expérience personnalisée et de vous recommander des films qui correspondent parfaitement à vos préférences.</p>
         <button class="genreSection" :class="{ selected: isSelected(genre.genreId), disabled: isDisabled(genre.genreId) }" v-for="genre in genresSections" :key="genre.genreId"  @click="clickedGenre(genre.genreId) ">
            <label :for="genre.genreId">{{ genre.name }} </label>
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