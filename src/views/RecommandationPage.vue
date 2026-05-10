<script setup lang="ts">
import "@/assets/filmCard.css";
import "@/assets/recommendation.css";
import { RouterLink} from 'vue-router';
import type { Schema } from '../../amplify/data/resource';
import { onMounted, ref } from 'vue';
import { generateClient } from 'aws-amplify/data';
import { getCurrentUser} from 'aws-amplify/auth';
import {handleImageError} from "@/utils/defaultPoster";

const client = generateClient<Schema>();
const moviesIds = ref<any>([]);
const movies = ref<Array<Schema['Movie']["type"]>>([]);
const identifiant = ref<string | null>(null);
const loading= ref(true);
        
onMounted(async () => {
    try {
        const user = await getCurrentUser();
        identifiant.value = user.userId;
        const { data, errors } = await client.queries.getRecommendations({
        userId: identifiant.value ?? "",
        })
        console.log("erreurs:",errors);
      moviesIds.value=data?.recommendations;

      // récuperer les films complets
      const moviesData = await Promise.all(moviesIds.value.map((movieId:string) => client.models.Movie.get({ id: movieId})))
      movies.value = moviesData.map(res => res.data).filter(movie => movie !== undefined)

    } catch (error) {
      console.error("Error fetching movies:", error);
    } finally{
      loading.value=false;
    }
}); 

</script>


<template>
  <div class="page">
  <div v-if="loading" class="condition">
    Loading...<font-awesome-icon icon="fa-solid fa-hourglass" style="color: white;" />
  </div>
  <div v-else-if="movies.length===0" class="condition-2">
      No recommendation for you <font-awesome-icon icon="fa-solid fa-xmark" style="color: brown;" />
      <p>try rating more movies</p>
  </div>
<div v-else class="container">
   <router-link v-for="movie in movies" :key="movie.movieId" :to=" { name :'details', params:{ id:movie.movieId }}" 
   class="movie-card">
    <img :src="movie.posterPath? 'https://image.tmdb.org/t/p/w500' + movie.posterPath :''"
      :alt="movie.title ?? ''" 
      @error="handleImageError"/>
    <div class="movie-info">
      <p class="movie-title">{{ movie.title }}</p>
      <p class="movie-meta">★ {{ movie.voteAverage }}</p>
    </div>     

  </router-link>
</div>
</div>
</template>
