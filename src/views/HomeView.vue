<script setup lang="ts">
import "@/assets/filmCard.css";
import {ref, computed , onMounted} from 'vue';
import Pagination from '../components/Pagination.vue';
import type { Schema } from "../../amplify/data/resource";
import { generateClient } from 'aws-amplify/api';
import SearchBar from '@/components/SearchBar.vue';
import { textSpanContainsPosition } from 'typescript';
import {handleImageError} from "@/utils/defaultPoster";


const client = generateClient <Schema>();

const movies = ref<Array<Schema['Movie']["type"]>>([]);
const currentPage = ref(1);
const itemsPerPage = 70;

const moviesByPage = ref<Record<number, Array<Schema['Movie']["type"]>>>({});
const nextTokens = ref<Record<number, string | null>>({});



async function loadMoviesPage(page: number) {
   try {
    // ne pas chargé si l'utilisateur recherche
   // if (isSearching.value) return;
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

//recherche
const searchResults=ref<Array<Schema['Movie']["type"]>>([]);
const isSearching=ref(false);

async function searchMovies(query:string) {
  const q=query.toLocaleLowerCase().trim();
    let results:any[]=[];
    let nextToken:string | null=null;
  if(!q){
    isSearching.value=false;
    searchResults.value=[];
    return;
  }
  isSearching.value=true;
do{
    const {data,nextToken:newNextToken}:{data:any[]; nextToken?:string|null;} =await client.models.Movie.list({
      filter:{
        or:[
        {title: {contains:q}},
        {keywords: {contains:q}},
      ]
      },
      limit:2000,
      nextToken,
    });
    results = [...results, ...(data ?? [])];
    nextToken=newNextToken?? null;
    console.log(data);
  }while(nextToken)
searchResults.value=results;
}


function getImageUrl(posterPath: any) {
   const path = String(posterPath || '').trim();
  if (!posterPath || posterPath === 'null' || posterPath === 'undefined' || posterPath === '') return '/defaultPoster.webp';
  if (posterPath.startsWith('/')) {
    return `https://image.tmdb.org/t/p/w500${path}`;
  }
  return posterPath;
}



</script>


<template>
<div class="page">
  <div class="haut-page">
    <div>
    <h1>Welcome to Recomodo</h1>
    </div>
    <div class="Search">
    <SearchBar @search="searchMovies"/>
    </div>
  </div>
<div class="content">
<div class="container">
    <RouterLink
       v-for="movie in isSearching? searchResults:movies"
        :key="movie.movieId"
        :to=" { name: 'details', params: { id: movie.movieId } }"
         
        class="movie-card"
    >
        <img
            :src="'https://image.tmdb.org/t/p/w200' + movie.posterPath"
           
            :alt="movie.title"
            @error="handleImageError"
       />
        <div class="movie-info">
             <p class="movie-title">{{ movie.title }}</p>
             <p class="movie-meta">★ {{ movie.voteAverage }}</p>
        </div>
    </RouterLink>
</div>

<div v-if="!isSearching" class="pagination-wrapper">
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
    /*margin-top: auto;*/
    padding: 2rem 0;
    justify-content: center;
    display: flex;
}

html, body {
    height: 100%;
}

h1{
    color: white;
    margin: 0;
}

.haut-page{
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items:flex-end;
  padding-inline: 2.3rem;
  padding-block:2rem;
}

</style>
