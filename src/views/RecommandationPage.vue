<script setup lang="ts">
import { useRouter } from 'vue-router';
import type { Schema } from '../../amplify/data/resource';
import { onMounted, ref } from 'vue';
import { generateClient } from 'aws-amplify/data';
import { getCurrentUser} from 'aws-amplify/auth';

const router = useRouter(); 


const client = generateClient<Schema>();
const moviesIds = ref<any>([]);
const movies = ref<Array<Schema['Movie']["type"]>>([]);
const identifiant = ref<string | null>(null);
        
onMounted(async () => {
    try {
        const user = await getCurrentUser();
        identifiant.value = user.userId;
        const { data, errors } = await client.queries.getRecommendations({
        //userId: identifiant.value ??
        userId:"tmdb_150",
        })
      moviesIds.value=data?.recommendations;

      // récuperer les films complets
      const moviesData = await Promise.all(moviesIds.value.map((movieId:string) => client.models.Movie.get({ id: movieId})))
      movies.value = moviesData.map(res => res.data).filter(movie => movie !== undefined)
      console.log("Recommendations fetched:", moviesIds.value);
      console.log("data:", data);
      console.log("errors:", errors);
    } catch (error) {
      console.error("Error fetching movies:", error);
    }
}); 


function filmDetails(movieId:string){
    router.push(`/movie/details/${movieId}`);
}



</script>


<template>
<div class="container">
<div  class="movie-card"v-for="(movie) in movies" :key="movie.movieId" @click="filmDetails(movie.movieId)">
    <img :src="movie.posterPath? 'https://image.tmdb.org/t/p/w500' + movie.posterPath :''"
         :alt="movie.title ?? ''" />
    <div class="movie-info">
       <span class="movie-title">{{ movie.title }}</span>
       <span class="movie-meta">{{ movie.voteAverage }}<font-awesome-icon icon="fa-solid fa-star" size="xs" style="color: #f5c518;" /></span>
    </div>   
   </div>
</div>
</template>

<style scoped>
.title{
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}


</style>