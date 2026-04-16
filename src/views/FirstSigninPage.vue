<script setup lang="ts">
//récuperer le liste des genres dans un tableau
import { ref, onMounted ,computed} from 'vue';
import { useRouter } from 'vue-router';
const router = useRouter();
//api
import type {Schema} from "../../amplify/data/resource";
import { generateClient } from 'aws-amplify/data';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import Rating from '@/components/Rating.vue';

const client = generateClient<Schema>();
const movies = ref<Array<Schema['Movie']["type"]>>([]);
const genres=ref<Array<Schema['Genre']["type"]>>([]);
const profile = ref<Schema['UserProfile']["type"]|null>(null);

const listGenresQuery = `
  query ListGenres {
    listGenres{
      items {
        genreId
        name
      }
    }
  }
`;


const listMoviesQuery = `
  query ListMovies {
    listMovies(limit: 18) {
      items {
        movieId
        title
        voteAverage
        posterPath
        genres
      }
    }
  }
`;

onMounted(async () => {
    try{
  const resg = await client.graphql({
    query: listGenresQuery
  });
  console.log("FULL RES:", resg);
  const items = resg.data?.listGenres?.items;
  genres.value = Array.isArray(items) ? items : [];
}catch(error){
  console.error("Error fetching genres:", error);
}
});

onMounted(async () => {
    try{
  const res = await client.graphql({
    query: listMoviesQuery
  });
  console.log("FULL RES:", res);
  const items = res.data?.listMovies?.items;
  movies.value = Array.isArray(items) ? items : [];
}catch(error){
  console.error("Error fetching movies:", error);
}
});

function getGenres(id:number|null|undefined) {
   if(!id){
      return"";
   }else{
      const genre = genres.value.find(g => Number(g.genreId) === Number(id));
      return genre ? genre.name : "";
      
   }
}
//const rating = ref<number[]>([])
const ratings = ref<Record<string, number>>({})
const ratingsCount = computed(() =>
  Object.values(ratings.value).filter(r => r > 0).length
)

function submit() {
  console.log("Ratings submitted:", ratings.value);
  // envoi avec api aux base dynamodb
  // ensuite redirection vers la page d'accueil
  redirected();
}
function redirected(){
   router.push('/');
}
</script>


<template>
   
   <h4 class="genre">please rate at least 10 movies from the list for a better recommendation</h4>
<div class="formContainer">
  <div  class="blockMovie"v-for="(movie,index) in movies" :key="movie.movieId">
    <img :src="movie.posterPath? 'https://image.tmdb.org/t/p/w500' + movie.posterPath :''"
         :alt="movie.title ?? ''" />
         <div class="formSubContainer">
    <div class="discriptionForm">
       <p>{{ movie.title }}</p>
       <p>{{ movie.voteAverage }} <font-awesome-icon icon="fa-solid fa-star" size="xs" style="color: white;" /></p>
    </div> 
    <div class="genres" v-if="movie.genres">
      <div class="genre"  v-for="genreId in movie.genres" :key="genreId ?? ''">
      {{getGenres(genreId)}}
      </div>
    </div>
    <div class="rating">
     <Rating v-model="ratings[movie.movieId]" />
     </div>
     </div>
  </div>
    <p v-if="ratingsCount<10" style="color: brown;">
      Minimum 10 films requis ({{ ratingsCount }}/10)
    </p>
    <button :disabled="ratingsCount<10" @click="submit">
      Submit
    </button>
</div> 

</template>

<style scoped>

.formContainer{
   display: flex;
   flex-direction: row;
   flex-wrap:wrap;
   gap:40px;
   padding-inline: 2rem;         /*inline padding*/
   justify-content: center;
}
.blockMovie{
   display: flex;
   flex-direction: row;
   justify-content: space-around;
   background-color: rgb(61, 9, 67);
   border-radius: 14px;
   box-shadow: 20px 20px 20px rgba(239, 162, 239, 0.219);
   height: 200px;
   width : 550px;
}

.blockMovie img{
   height: 150px;
   width: 100px;
   display: flex;
   align-self: center;

}
.discriptionForm{
   display: flex; 
   width:100%;
   justify-content: space-between;
}

.formSubContainer{
   display: flex;
   flex-direction: column;
   justify-content: space-between;
   padding-block: 1rem;
}
.genres{
   display:flex;
   flex-direction: row;
}

.genre{
   display: inline;
   color: rgb(239, 162, 239);
   background-color: rgba(128, 0, 122, 0.153);
   border-color:rgb(239, 162, 239);
   border: 1px solid;
   border-radius: 12px;
   padding: 2px 6px;
}

button:disabled{
   background-color: rgba(32, 32, 32, 0.568);
   border: 1px solid rgba(32, 32, 32, 0.468);
   cursor: not-allowed;
}
button{
   background-color: rgb(61, 9, 67);
   border: 1px solid rgb(61, 9, 67);
   cursor: pointer;
}

</style>