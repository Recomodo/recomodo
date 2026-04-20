<script setup lang="ts">
import { useRouter } from 'vue-router';
import type { Schema } from '../../amplify/data/resource';
import { onMounted, ref } from 'vue';
import { generateClient } from 'aws-amplify/data';
import { getCurrentUser} from 'aws-amplify/auth';
const router = useRouter();


const client = generateClient<Schema>();
const movies = ref<Array<Schema['Movie']["type"]>>([]);

const identifiant = ref<string | null>(null);
onMounted(async () => {
  const user = await getCurrentUser();
  identifiant.value = user.userId;
});

/*onMounted(async () => {
    try {
      const { data, errors } = await client.queries.getRecommendations({
        userId: identifiant.value ?? "",
      })
      movies.value=data ?? [];
    } catch (error) {
      console.error("Error fetching movies:", error);
    }
});*/
onMounted(async () => {
    try {
      const { data, errors } = await client.models.Movie.list({
        limit: 20
      })
      movies.value=data ?? [];
    } catch (error) {
      console.error("Error fetching movies:", error);
    }
});

function filmDetails(movieId:string){
    router.push(`/movie/details/${movieId}`);
}


</script>


<template>
<div class="recommendationsContainer">
<div  class="movie"v-for="(movie) in movies" :key="movie.movieId" @click="filmDetails(movie.movieId)">
    <img :src="movie.posterPath? 'https://image.tmdb.org/t/p/w500' + movie.posterPath :''"
         :alt="movie.title ?? ''" />
    <div class="discription">
       <p>{{ movie.title }}</p>
       <p>{{ movie.voteAverage }}</p>
    </div>   
   </div>
</div>
</template>
