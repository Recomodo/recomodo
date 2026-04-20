<script setup lang="ts">
//récuperer le liste des genres dans un tableau
import { ref, onMounted ,computed} from 'vue';
import { useRouter } from 'vue-router';
const router = useRouter();
//api
import type {Schema} from "../../amplify/data/resource";
import { generateClient } from 'aws-amplify/data';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { getCurrentUser } from 'aws-amplify/auth';

import Rating from '@/components/Rating.vue';

const email = ref<string | null>(null);
const identifiant = ref<string | null>(null);
onMounted(async () => {
  const user = await getCurrentUser();
  email.value = user.signInDetails?.loginId ?? null;
  identifiant.value = user.userId;
});

const client = generateClient<Schema>();
const movies = ref<Array<Schema['Movie']["type"]>>([]);
const genres=ref<Array<Schema['Genre']["type"]>>([]);

const moviesList=["11249","27205","155","101","293660","10625","620","185","313369","8587","10674","648","12477","28","348","803","10654","273248"]


/*onMounted(async () => {
    try {
      const [moviesData,genresData] = await Promise.all([
        client.models.Movie.list({ limit: 18 }),
        client.models.Genre.list()
      ]);
      movies.value = moviesData.data ?? [];
      genres.value = genresData.data ?? [];
    } catch (error) {
      console.error("Error fetching movies or genres:", error);
    }
});*/


function getGenres(id:number|null|undefined) {
   if(!id){
      return"";
   }else{
      const genre = genres.value.find(g => Number(g.genreId) === Number(id));
      return genre ? genre.name : "";
      
   }
}
const ratings = ref<Record<string, number>>({})
const ratingsCount = computed(() =>
  Object.values(ratings.value).filter(r => r > 0).length
)

async function submit() {
  console.log("Ratings submitted:", ratings.value);
  // envoi avec api aux base dynamodb
  // ensuite redirection vers la page d'accueil
await Promise.all(Object.entries(ratings.value).map(([movieId, rating]) =>   //stocker les valeurs des notes 
  client.models.Rating.create({
    userId: identifiant.value ?? "",
    movieId,
    rating
  })
));

  if (identifiant.value){
  await client.models.UserProfile.update({
    id: identifiant.value,
    hasCompleted:true
  })
  }
  redirected();
}
function redirected(){
   router.push('/');
}

onMounted(async () => {
    try {
      const { data, errors } = await client.models.Genre.list({
        limit: 20
      });
      genres.value=data ?? [];
    } catch (error) {
      console.error("Error fetching genres:", error);
    }
});

onMounted(async () => {
    try {
      const responses = await Promise.all(moviesList.map(movieId =>
        client.models.Movie.get({ id: movieId })
      ));
      movies.value = responses
        .map((response) => response.data)
        .filter(
          (
            movie
          ): movie is NonNullable<(typeof responses)[number]["data"]> => movie !== null
        );
    } catch (error) {
      console.error("Error fetching movies:", error);
    }
});
</script>


<template>
   
   <p class="pform">Please rate at least 10 movies from the list for a better recommendation</p>
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

.pform{
  color: rgb(239, 162, 239);
  font-weight: 600;
}

</style>
