<script setup lang="ts">
//récuperer le liste des genres dans un tableau
import { ref, onMounted } from 'vue';

//api
import type {Schema} from "../../amplify/data/resource";
import { generateClient } from 'aws-amplify/data';

interface Genre {
   id: number;
   genreId: number;
   name: string;
}

interface GenreSection {
   id: number;
   genre1: Genre;
   genre2: Genre;
   genre3: Genre;
}
const genres : Genre[] =[
      {
   id: 1,
   genreId: 1,
   name: "fantasy"
   },
   {
      id: 2,
      genreId: 2,
      name: "action"
   },
   {
      id: 3,
      genreId: 3,
      name: "comedy"
   },
   {
      id: 4,
      genreId: 4,
      name: "horror"
   },
   {
      id: 5,
      genreId: 5,
      name: "science fiction"
   },{
      id:6,
      genreId:6,
      name: "romance"
   },
   {
      id:7,
      genreId:7,
      name: "thriller"
   },
   {
      id:8,
      genreId:8,
      name: "animation"
   },
   {
      id:9,
      genreId:9,
      name: "adventure"
   },
   {
      id:10,
      genreId:10,
      name: "documentary"
   },
   {
      id:11,
      genreId:11,
      name: "mystery"
   },
   {
      id:12,
      genreId:12,
      name: "crime"
   }

]

const genresSections: GenreSection[] = [
   {
      id:1,
      genre1: genres[0],
      genre2: genres[1],
      genre3: genres[2]
   },
   {
      id:2,
      genre1: genres[3],
      genre2: genres[4],
      genre3: genres[5]
   },
   {
      id:3,
      genre1: genres[6],
      genre2: genres[7],
      genre3: genres[8]
   },
   {
      id:4,
      genre1: genres[9],
      genre2: genres[10],
      genre3: genres[11]
   }
];


/*const tabFilms=[
   {
      id:title
   }

]*/

/*
const client = generateClient<Schema>();
const genresSections = ref<Array<Schema['Genre']["type"]>>([]);


onMounted(async()=>{
   const{data}=await client.models.Genre.list();
   console.log("GENRES:", data);
   genresSections.value=data;
})
*/
const maxSelection = 3;
const selectedGenres = ref<number[]>([]);

function clickedGenreSection(genreId: number) {
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
      <div class="genresContainer">
         <button class="genreSection" :class="{ selected: isSelected(genreSection.id), disabled: isDisabled(genreSection.id) }" v-for="genreSection in genresSections" :key="genreSection.id"  @click="clickedGenreSection(genreSection.id) ">
            <label :for="String(genreSection.genre1.genreId)">{{ genreSection.genre1.name }}, </label>
            <label :for="String(genreSection.genre2.genreId)">{{ genreSection.genre2.name }}, </label>
            <label :for="String(genreSection.genre3.genreId)">{{ genreSection.genre3.name }}</label>
         </button>
      </div>
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
.genreSection{
   border: 1px solid black;
   border-radius: 17px;
   padding: 10px;
   margin: 5px;
   cursor: pointer;
   display: flex;
   height: 300px;
   width:500px
}
.genresContainer{
   display: flex;
   flex-direction: column;
   padding-left: 2rem;
   gap:30px;

}

button:hover{
   transform: scale(1.03);
}
</style>