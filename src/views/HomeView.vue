<script setup lang="ts">
import {ref, computed , onMounted} from 'vue';
import Pagination from '../components/Pagination.vue';
import type { Schema } from "../../amplify/data/resource";
import { generateClient } from 'aws-amplify/api';

const client = generateClient <Schema>();

const movies = ref<Array<Schema['Movie']["type"]>>([]);
const currentPage = ref(1);
const itemsPerPage = 500;

const moviesByPage = ref<Record<number, Array<Schema['Movie']["type"]>>>({});
const nextTokens = ref<Record<number, string | null>>({});



async function loadMoviesPage(page: number) {
   try {
     if(moviesByPage.value[page]) {
        movies.value = moviesByPage.value[page];
        return;
      }

      let token=null;

      for (let i=1;i<page;i++){
        token = nextTokens.value[i];
        if(!token){
            break;
        }
      }

      const { data, nextToken} = await client.models.Movie.list({ limit: itemsPerPage, nextToken: token });
        moviesByPage.value[page] = data ?? [];
        nextTokens.value[page] = nextToken ?? null;
        movies.value = moviesByPage.value[page];
    } catch (error) {
        console.error("Error fetching movies for page " ,error);
    }  
}


onMounted(() => {
    loadMoviesPage(1);
});

function handlePageChange(page: number) {
    currentPage.value = page;
    loadMoviesPage(page);
}
</script>


<template>
<div class="page">
    <h1>Welcome to Recomodo</h1>
<div class="content">
<div class="container">
    <RouterLink
        v-for="(movie) in movies"
        :key="movie.movieId"
        :to=" { name: 'details', params: { id: movie.movieId } }"
         
        class="movie"
    >
        <img
            :src="'https://image.tmdb.org/t/p/w500' + movie.posterPath"
           
            :alt="movie.title"
       />
        <div class="discription">
            <p><strong><em>{{ movie.title }}</em></strong></p>
            <p><strong><em>{{ movie.voteAverage }}</em></strong></p>
        </div>
    </RouterLink>
</div>
<div class="pagination-wrapper">
    <Pagination 
        :currentPage="currentPage"
        @page-changed="handlePageChange"/>
</div>
</div>
</div>
</template>

<style scoped>
.page {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    
}

.pagination-wrapper {
    margin-top: auto;
    padding: 2rem 0;

    
    bottom: 20px;
    left:0;
    right:0;
    display: flex-end;
    justify-content: center;
    
    
}

html, body {
    height: 100%;
}

h1{
    color: white;
    margin: 0;
    padding-left: 4rem;
    padding-top: 2rem;
}

.movie {
  text-decoration: none; /* enlève le soulignement */
  color: inherit;        /* garde le texte blanc */
  display: block;
  cursor: pointer;
  transition: transform 0.2s;
}

img{
    width: 100px;
    height: 140px;
    display: block;
    justify-self: center;
    
}
.discription{
    display: flex;
    flex-direction:row;
    justify-content: space-around;
    align-items: center;
    font-size: small;
    position:relative;
    color: white;
}
.movie{
    height: 200px;
    width:150px;
    background-color:rgb(61,9,67);
    border-radius: 15px;
    padding-top: 15px;
    margin-top: 15px;
}

.container{
    display: grid;
    grid-template-columns: repeat(auto-fit, 150px);
    gap: 2rem;
    padding: 2rem 2rem;
    box-sizing: border-box;
    justify-content: start;
    margin-left: 1rem ;
    flex-grow: 1;
    align-self: start;
    height: 100%;

}


</style>