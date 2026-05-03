<script setup lang="ts">
import "@/assets/FirstSignIn.css";
import {handleImageError} from "@/utils/defaultPoster";
import { ref, onMounted ,computed} from 'vue';
import type {Schema} from "../../amplify/data/resource";
import { generateClient } from 'aws-amplify/data';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { getCurrentUser } from 'aws-amplify/auth';
import "@/assets/rating.css";
import Rating from "@/components/Rating.vue";


const email = ref<string | null>(null);
const identifiant = ref<string | null>(null);
const profile = ref<any>(null);
onMounted(async () => {
  const user = await getCurrentUser();
  email.value = user.signInDetails?.loginId ?? null;
  identifiant.value = user.userId;
});

const client = generateClient<Schema>();
const movies = ref<Array<Schema['Movie']["type"]>>([]);
const genres=ref<Array<Schema['Genre']["type"]>>([]);

const moviesList=["11249","27205","155","101","293660","10625","620","185","313369","8587","10674","648","12477","28","348","803","10654","273248"]



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
  // envoi avec api aux base dynamodb
  // ensuite redirection vers la page d'accueil
await Promise.all(Object.entries(ratings.value).map(([movieId, rating]) =>   //stocker les valeurs des notes 
  /*client.models.Rating.create({
    userId: identifiant.value ?? "",
    movieId,
    rating
  })*/
  client.mutations.updateUserRating({
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
location.href = '/'
}
onMounted(async () => {
    try {
      const { data} = await client.models.Genre.list({
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




// changer de films dans le cas ou il ne l'a pas vu 

const loadingMovie=ref<Record<string,boolean>>({});
const seenMoviesIds=ref<Set<string>>(new Set());

  movies.value.forEach(m=>{
    if(m.movieId){
      seenMoviesIds.value.add(m.movieId);
    }
  })

async function changeMovie(idMovieToChange:string){
//appeler la lambda 
try{
  loadingMovie.value[idMovieToChange]=true;
  seenMoviesIds.value.add(idMovieToChange);
  const index = movies.value.findIndex(m=>m.movieId === idMovieToChange);
  if(index === -1)return;
  const currentMovie = movies.value[index];
  const genreId= currentMovie.mainGenre;

  if(!genreId) return;

  const excludedIds=Array.from(seenMoviesIds.value);

    const{data, errors} = await client.queries.getMovieByGenre({
    genreId,
    excludedIds
  });

  //ajout de l'id du nouveau film dans exclus
  if(data?.movieId){
    seenMoviesIds.value.add(data.movieId);
  }

  console.log("erreur getMovieByGenre:",errors)
  if(errors || !data || !data.movieId){
    console.warn("aucun film trouvé");
    return;
  }
  if (!data.movieId || !data.title) {
  console.warn("Film invalide reçu de la lambda");
  return;
}
  movies.value[index]={
    ...currentMovie,
    ...data,
    movieId:data.movieId,
    title:data.title,
    voteAverage: Number(data.voteAverage)
  };

}catch (error){
  console.error("erreur changement de film:",error);
}finally{
  loadingMovie.value[idMovieToChange]=false;
}
}

</script>


<template>
<div class="pageContainer"> 
   <p class="pform">Please rate at least 10 movies from the list for a better recommendation</p>
  <div class="formContainer">
  
    <div  class="blockMovie"v-for="(movie,index) in movies" :key="movie.movieId">
      <div>
        <button class="autre" :disabled="ratings[movie.movieId]>0" @click="changeMovie(movie.movieId)"><font-awesome-icon icon="fa-solid fa-arrows-rotate" style="color:white;" /></button>
       <img :src="movie.posterPath? 'https://image.tmdb.org/t/p/w500' + movie.posterPath 
         :'/defaultPoster.webp'"
         :alt="movie.title"
         @error="handleImageError" />
      </div>
      <div class="formSubContainer">
        <div class="discriptionForm">
         <p class="title">{{ movie.title }}</p>
         <p>{{ movie.voteAverage }} <font-awesome-icon icon="fa-solid fa-star" size="xs" style="color: white;" /></p>
        </div> 
      <div class="Genres" v-if="movie.genres">
        <div class="Genre"  v-for="genreId in movie.genres" :key="genreId ?? ''">
          {{getGenres(genreId)}}
        </div>
      </div>
      <div class="rating">
          <Rating
          :notation="ratings[movie.movieId] || 0"
          @rate="(val) => ratings[movie.movieId] = val"
          />
    </div>
  </div>
</div>
</div>
  <div class="submit">
    <p v-if="ratingsCount<10" style="color: brown;">
      Minimum 10 movies required ({{ ratingsCount }}/10)
    </p>
    <span>
    <button :disabled="ratingsCount<10" @click="submit">
      Submit
    </button>
   </span>
  </div>
</div> 

</template>
