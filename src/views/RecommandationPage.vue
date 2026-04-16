<script setup lang="ts">
import { useRouter } from 'vue-router';
import type { Schema } from '../../amplify/data/resource';
import { onMounted, ref } from 'vue';
import { generateClient } from 'aws-amplify/data';
const router = useRouter();

const listMoviesQuery = `
  query ListMovies {
    listMovies(limit: 20) {
      items {
        movieId
        title
        voteAverage
        posterPath
      }
    }
  }
`;


const client = generateClient<Schema>();


const movies = ref<Array<Schema['Movie']["type"]>>([]);
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

/*const movies = ref<Array<Schema['Movie']["type"]>>([]);

function listMovies() {
  client.models.Movie.observeQuery().subscribe({
    next: ({ items, isSynced }) => {
      movies.value = items
     },
  }); 
}

onMounted(
  listMovies()
)*/


function filmDetails(movieId:string){
    router.push(`/movie/details/id:${movieId}`);
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
